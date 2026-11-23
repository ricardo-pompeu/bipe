#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Confere o catálogo e ícones realmente incorporados ao pacote da loja."""
import gzip
import sys
import xml.etree.ElementTree as ET
import gi

gi.require_version('Flatpak', '1.0')
from gi.repository import Flatpak, Gio

bundle = Flatpak.BundleRef.new(Gio.File.new_for_path(sys.argv[1]))
data = bundle.get_appstream()
assert data is not None, 'O Flatpak não contém catálogo AppStream.'
raw = data.get_data()
if raw.startswith(b'\x1f\x8b'):
    raw = gzip.decompress(raw)
root = ET.fromstring(raw)
component = next(c for c in root.iter('component') if c.findtext('id') == 'io.github.ricardo_pompeu.Bipe')
assert component.findtext('name') == 'Bipe'
assert component.findtext('developer/name') == 'Ricardo Pompeu'
assert component.find('description/p') is not None
assert len(component.findall('screenshots/screenshot')) == 3
for size in (64, 128):
    icon = bundle.get_icon(size)
    assert icon is not None and icon.get_data().startswith(b'\x89PNG'), f'Ícone {size} ausente.'
print('PASS: pacote contém nome, responsável, descrição, três capturas e ícones de 64/128 px.')
