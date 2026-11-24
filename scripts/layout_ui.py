#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Confere a venda em janela baixa com dados temporários, sem imprimir."""
from pathlib import Path
import os
import sys
import tempfile
import traceback
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory(prefix='bipe-layout-') as temporary:
    os.environ['XDG_DATA_HOME'] = temporary + '/data'
    os.environ['XDG_CACHE_HOME'] = temporary + '/cache'
    from bipe.ui import Application
    from gi.repository import Gio, GLib, Gtk
    app = Application()
    app.set_flags(Gio.ApplicationFlags.NON_UNIQUE)
    errors = []
    def step(callback):
        def run():
            try:
                callback()
            except BaseException as exc:
                errors.append(exc)
                traceback.print_exc()
                app.quit()
            return False
        GLib.timeout_add(600, run)
    def start():
        w = app.get_active_window()
        w.store.save_product('test', 'Produto de teste', 750, stock=5)
        w.refresh_products()
        assert Gtk.IconTheme.get_for_display(w.get_display()).has_icon('dialog-warning-symbolic')
        w.set_default_size(850, 490)
        step(empty)
    def check(name):
        w = app.get_active_window()
        assert w.get_height() <= 490, w.get_height()
        for widget in (w.scan, w.total, w.finish, w.cancel):
            ok, bounds = widget.compute_bounds(w)
            assert ok and bounds.get_y() >= 0 and bounds.get_y() + bounds.get_height() <= w.get_height(), (name, widget, bounds)
            assert bounds.get_height() >= 20
        assert w.cart_views.get_height() >= 50
        snapshot = Gtk.Snapshot()
        Gtk.WidgetPaintable.new(w).snapshot(snapshot, w.get_width(), w.get_height())
        texture = w.get_renderer().render_texture(snapshot.to_node(), None)
        texture.save_to_png('/tmp/bipe-sale-' + name + '.png')
    def empty():
        check('empty')
        w = app.get_active_window()
        for i in range(12):
            w.cart.add(w.store.save_product(str(i), 'Produto ' + str(i), 750))
        w.refresh_cart()
        w.set_default_size(640, 420)
        step(populated)
    def populated():
        check('populated')
        app.get_active_window().cart.clear()
        app.quit()
        print('PASS: leitor, total e ações visíveis em 850×490 e 640×420, com aviso e lista rolável.')
    step(start)
    app.run([])
    if errors:
        raise SystemExit(1)
