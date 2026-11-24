#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compõe o catálogo do único aplicativo com libappstream e ícones com librsvg."""
from pathlib import Path
import sys
import cairo
import gi

gi.require_version('AppStream', '1.0')
gi.require_version('Rsvg', '2.0')
from gi.repository import AppStream, Gio, Rsvg

APP_ID = 'io.github.ricardo_pompeu.Bipe'
prefix = Path(sys.argv[1])
source = prefix / 'share/metainfo' / f'{APP_ID}.metainfo.xml'
metadata = AppStream.Metadata.new()
metadata.set_format_style(AppStream.FormatStyle.METAINFO)
metadata.parse_file(Gio.File.new_for_path(str(source)), AppStream.FormatKind.XML)
component = metadata.get_component()
assert component is not None and component.get_id() == APP_ID
stock = AppStream.Icon.new()
stock.set_kind(AppStream.IconKind.STOCK)
stock.set_name(APP_ID)
component.add_icon(stock)

svg = Rsvg.Handle.new_from_file(str(prefix / 'share/icons/hicolor/scalable/apps' / f'{APP_ID}.svg'))
for size in (64, 128):
    folder = prefix / 'share/app-info/icons/flatpak' / f'{size}x{size}'
    folder.mkdir(parents=True, exist_ok=True)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    rect = Rsvg.Rectangle()
    rect.x, rect.y, rect.width, rect.height = 0, 0, size, size
    svg.render_document(cairo.Context(surface), rect)
    surface.write_to_png(str(folder / f'{APP_ID}.png'))
    icon = AppStream.Icon.new()
    icon.set_kind(AppStream.IconKind.CACHED)
    icon.set_name(f'{APP_ID}.png')
    icon.set_width(size)
    icon.set_height(size)
    component.add_icon(icon)

catalog = AppStream.Metadata.new()
catalog.set_format_style(AppStream.FormatStyle.CATALOG)
catalog.set_origin(APP_ID)
catalog.add_component(component)
destination = prefix / 'share/app-info/xmls' / f'{APP_ID}.xml.gz'
destination.parent.mkdir(parents=True, exist_ok=True)
assert catalog.save_catalog(str(destination), AppStream.FormatKind.XML)
print('Catálogo AppStream e ícones gerados.')
