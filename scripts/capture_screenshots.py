#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Capturas reais, com dados temporários de demonstração; nenhuma impressão."""
from pathlib import Path
import os
import sys
import tempfile
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory(prefix='bipe-capturas-') as temp:
    os.environ['XDG_DATA_HOME'] = temp + '/data'
    os.environ['XDG_CACHE_HOME'] = temp + '/cache'
    from bipe.ui import Application
    from bipe.core import Cart
    from gi.repository import Gio, GLib, Gtk

    app = Application()
    app.set_flags(Gio.ApplicationFlags.NON_UNIQUE)
    output = Path(__file__).resolve().parents[1] / 'data/screenshots'
    output.mkdir(exist_ok=True)
    errors = []

    def guard(function):
        def run():
            try:
                function()
            except Exception as error:
                errors.append(error)
                traceback.print_exc()
                app.quit()
            return False
        return run

    def capture(name):
        window = app.get_active_window()
        paint = Gtk.WidgetPaintable.new(window)
        snapshot = Gtk.Snapshot()
        paint.snapshot(snapshot, window.get_width(), window.get_height())
        node = snapshot.to_node()
        if node is None:
            raise RuntimeError('A janela precisa estar visível em um display gráfico.')
        texture = window.get_renderer().render_texture(node, None)
        texture.save_to_png(str(output / name))

    def start():
        window = app.get_active_window()
        rice = window.store.save_product('7891000000001', 'Arroz branco 1 kg', 750, stock=12)
        beans = window.store.save_product('7891000000002', 'Feijão carioca 1 kg', 890, stock=10)
        window.store.save_product('7891000000003', 'Café torrado 250 g', 1290)
        cart = Cart()
        for product in (rice, rice, beans):
            cart.add(product)
        window.store.checkout(cart, 'PIX')
        for product in (rice, rice, beans):
            window.cart.add(product)
        window.refresh_cart()
        window.refresh_products()
        window.scan.set_position(0)
        GLib.timeout_add(400, guard(sell))

    def sell():
        capture('vender.png')
        app.get_active_window().stack.set_visible_child_name('products')
        GLib.timeout_add(400, guard(products))

    def products():
        capture('produtos.png')
        app.get_active_window().stack.set_visible_child_name('closing')
        GLib.timeout_add(400, guard(closing))

    def closing():
        capture('fechamento.png')
        app.get_active_window().cart.clear()
        app.quit()
        print('Capturas geradas com dados de demonstração.')

    GLib.timeout_add(700, guard(start))
    app.run([])
    if errors:
        raise SystemExit(1)
