#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fluxo de estoque da interface, isolado e sem impressão física."""
from pathlib import Path
import os
import sys
import tempfile
import traceback
sys.path.insert(0, os.environ.get('BIPE_TEST_PACKAGE', str(Path(__file__).resolve().parents[1])))

with tempfile.TemporaryDirectory(prefix='bipe-estoque-ui-') as temporary:
    os.environ['XDG_DATA_HOME'] = temporary + '/data'
    os.environ['XDG_CACHE_HOME'] = temporary + '/cache'
    from bipe.ui import Application
    from gi.repository import Adw, Gio, GLib, Gtk
    app = Application()
    app.set_flags(Gio.ApplicationFlags.NON_UNIQUE)
    errors = []

    def walk(widget):
        yield widget
        child = widget.get_first_child()
        while child:
            yield from walk(child)
            child = child.get_next_sibling()

    def find(kind, title):
        dialog = app.get_active_window().get_visible_dialog()
        return next(w for w in walk(dialog) if isinstance(w, kind) and w.get_title() == title)

    def click(title):
        dialog = app.get_active_window().get_visible_dialog()
        next(w for w in walk(dialog) if isinstance(w, Gtk.Button) and w.get_label() == title).emit('clicked')

    def step(callback):
        def run():
            try:
                callback()
            except BaseException as exc:
                errors.append(exc)
                traceback.print_exc()
                app.quit()
            return False
        GLib.timeout_add(400, run)

    def register():
        window = app.get_active_window()
        assert not window.stock_banner.get_revealed()
        window.scan.set_text('arroz')
        window.scan.emit('activate')
        find(Adw.EntryRow, 'Nome do produto').set_text('Arroz 1 kg')
        find(Adw.EntryRow, 'Preço de venda (R$)').set_text('7,50')
        assert not find(Adw.SpinRow, 'Quantidade disponível').get_visible()
        find(Adw.SwitchRow, 'Acompanhar quantidade').set_active(True)
        assert find(Adw.SpinRow, 'Quantidade disponível').get_visible()
        find(Adw.SpinRow, 'Quantidade disponível').set_value(3)
        find(Adw.SpinRow, 'Avisar quando restarem').set_value(2)
        click('Salvar e adicionar')
        assert window.store.product('arroz').stock == 3
        step(checkout)

    def checkout():
        window = app.get_active_window()
        window.scan.set_text('arroz')
        window.scan.emit('activate')
        assert window.store.product('arroz').stock == 3
        window.printer.print_receipt = lambda parent, sale, path, callback: callback(None)
        window.checkout()
        click('Concluir e imprimir')
        assert window.store.product('arroz').stock == 1
        assert window.stock_banner.get_revealed()
        assert window.closing_amount_value.get_label() == 'R$ 15,00'
        step(reprint)

    def reprint():
        window = app.get_active_window()
        click('Imprimir')
        assert window.store.product('arroz').stock == 1
        window.get_visible_dialog().close()
        step(closing)

    def closing():
        window = app.get_active_window()
        window.stack.set_visible_child_name('closing')
        assert window.closing_amount_value.get_label() == 'R$ 15,00'
        row = window.closing_product_list.get_first_child()
        assert row.get_subtitle() == '2 × R$ 7,50'
        window.product_dialog(product=window.store.product('arroz'))
        step(restock)

    def restock():
        window = app.get_active_window()
        assert find(Adw.SpinRow, 'Quantidade disponível').get_value() == 1
        find(Adw.SpinRow, 'Quantidade disponível').set_value(12)
        click('Salvar')
        assert not window.stock_banner.get_revealed()
        step(disable)

    def disable():
        window = app.get_active_window()
        window.product_dialog(product=window.store.product('arroz'))
        find(Adw.SwitchRow, 'Acompanhar quantidade').set_active(False)
        click('Salvar')
        assert window.store.product('arroz').stock is None
        print('PASS: estoque opcional, venda, baixa única, alerta, reimpressão, fechamento em reais, reposição e desativação.')
        app.quit()

    def exception_hook(kind, value, tb):
        errors.append(value)
        traceback.print_exception(kind, value, tb)
    sys.excepthook = exception_hook
    step(register)
    app.run([])
    if errors:
        raise SystemExit(1)
