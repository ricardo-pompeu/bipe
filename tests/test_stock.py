from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from bipe.core import Cart, MAX_UNITS, SCHEMA, Store


class StockTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / 'db.sqlite3')
        self.product = self.store.save_product('arroz', 'Arroz', 750, stock=8, low_stock=5)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def cart(self, quantity=1):
        cart = Cart()
        for _ in range(quantity):
            cart.add(self.product)
        return cart

    def test_stock_is_optional_and_cart_does_not_change_it(self):
        free = self.store.save_product('cafe', 'Café', 1290)
        self.assertIsNone(free.stock)
        cart = self.cart(3)
        cart.clear()
        self.assertEqual(self.store.product('arroz').stock, 8)
        self.assertEqual(self.store.low_stock_products(), [])

    def test_checkout_decrements_once_and_alerts_at_threshold(self):
        cart = self.cart(3)
        sale = self.store.checkout(cart, 'PIX')
        self.assertEqual(self.store.product('arroz').stock, 5)
        self.assertEqual(self.store.low_stock_products()[0].id, self.product.id)
        self.assertEqual(self.store.checkout(cart, 'PIX'), sale)
        self.store.sale(sale)  # Consultar/reimprimir lê a mesma venda.
        self.assertEqual(self.store.product('arroz').stock, 5)

    def test_low_stock_does_not_block_and_preserves_negative_balance(self):
        self.store.checkout(self.cart(10), 'Dinheiro')
        self.assertEqual(self.store.product('arroz').stock, -2)
        self.assertEqual(self.store.low_stock_products()[0].stock, -2)
        self.assertEqual(self.store.sale(1)['total'], 7500)

    def test_edit_preserves_count_and_can_disable_tracking(self):
        self.store.checkout(self.cart(3), 'PIX')
        saved = self.store.save_product('arroz', 'Arroz novo', 900, self.product.id)
        self.assertEqual(saved.stock, 5)
        self.assertEqual(saved.low_stock, 5)
        saved = self.store.save_product('arroz', 'Arroz novo', 900, self.product.id, stock=None)
        self.assertIsNone(saved.stock)
        self.assertEqual(self.store.low_stock_products(), [])
        self.store.checkout(self.cart(), 'PIX')
        self.assertIsNone(self.store.product('arroz').stock)

    def test_failed_stock_update_rolls_back_sale_and_every_product(self):
        beans = self.store.save_product('feijao', 'Feijão', 890, stock=10)
        cart = self.cart()
        cart.add(beans)
        with self.store.db:
            self.store.db.execute(f"""CREATE TRIGGER fail_stock BEFORE UPDATE OF stock ON products
                WHEN NEW.id={beans.id} BEGIN SELECT RAISE(ABORT,'falha de teste'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.checkout(cart, 'PIX')
        self.assertEqual(self.store.product('arroz').stock, 8)
        self.assertEqual(self.store.product('feijao').stock, 10)
        self.assertEqual(len(self.store.recent()), 0)
        with self.store.db:
            self.store.db.execute('DROP TRIGGER fail_stock')
        self.store.checkout(cart, 'PIX')
        self.assertEqual(self.store.product('arroz').stock, 7)

    def test_backup_and_reopen_keep_optional_stock(self):
        self.store.checkout(self.cart(3), 'PIX')
        backup = self.root / 'backup.sqlite3'
        self.store.backup(backup)
        self.store.save_product('arroz', 'Arroz', 750, self.product.id, stock=20, low_stock=2)
        self.store.restore(backup)
        self.store.close()
        self.store = Store(self.root / 'db.sqlite3')
        product = self.store.product('arroz')
        self.assertEqual((product.stock, product.low_stock), (5, 5))

    def legacy_database(self, path):
        with closing(sqlite3.connect(path)) as db:
            db.executescript(SCHEMA)
            with db:
                db.execute("INSERT INTO products(barcode,name,price) VALUES('antigo','Antigo',100)")
        return path

    def test_migrates_existing_v1_and_preserves_original_copy(self):
        path = self.legacy_database(self.root / 'legacy.sqlite3')
        migrated = Store(path)
        try:
            self.assertIsNone(migrated.product('antigo').stock)
            self.assertEqual(migrated.db.execute('PRAGMA user_version').fetchone()[0], 2)
            before = list(self.root.glob('antes-estoque-*.sqlite3'))
            self.assertTrue(before)
            with closing(sqlite3.connect(before[0])) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 1)
        finally:
            migrated.close()

    def test_restores_v1_backup_into_current_schema(self):
        backup = self.legacy_database(self.root / 'old-backup.sqlite3')
        self.store.restore(backup)
        self.assertIsNone(self.store.product('arroz'))
        self.assertIsNone(self.store.product('antigo').stock)
        self.assertEqual(self.store.db.execute('PRAGMA user_version').fetchone()[0], 2)

    def test_invalid_stock_is_rejected(self):
        for stock in (True, 1.2, '3', MAX_UNITS + 1):
            with self.subTest(stock=stock), self.assertRaises(ValueError):
                self.store.save_product('x', 'Inválido', 100, stock=stock)
        for limit in (-1, True, 1.5):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.store.save_product('x', 'Inválido', 100, low_stock=limit)

    def test_blank_quantity_disables_and_zero_tracks(self):
        from bipe.core import parse_stock
        self.assertIsNone(parse_stock('  '))
        self.assertEqual(parse_stock('0'), 0)
        self.assertEqual(parse_stock('12'), 12)
        self.assertEqual(parse_stock('-2'), -2)
        for text in ('1,5', '1.5', '--2', 'abc', '٣', '1000000000'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_stock(text)

    def test_global_limit_applies_to_all_products_and_is_saved(self):
        self.assertEqual(self.store.stock_warning_limit, 5)
        self.store.save_product('arroz', 'Arroz', 750, self.product.id, stock=6, low_stock=100)
        self.store.save_product('feijao', 'Feijão', 890, stock=7, low_stock=0)
        self.assertEqual(self.store.low_stock_products(), [])
        self.store.configure(stock_warning_limit=7)
        self.assertEqual(len(self.store.low_stock_products()), 2)
        self.store.close()
        self.store = Store(self.root / 'db.sqlite3')
        self.assertEqual(self.store.stock_warning_limit, 7)
        self.assertEqual(len(self.store.low_stock_products()), 2)
        for limit in (-1, '5', 1.5, True):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.store.configure(stock_warning_limit=limit)
