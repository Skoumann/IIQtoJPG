# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Define the paths to include
project_dir = os.path.abspath('.')
net6_dir = os.path.abspath('net6.0')
dest_dir = os.path.abspath('dest')

# Function to collect all files in a directory
def collect_data_files(directory, target_folder):
    data_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(target_folder, os.path.relpath(root, directory))
            data_files.append((src, dst))
    return data_files

# Collect data files from net6.0 and dest directories
datas = collect_data_files(net6_dir, 'net6.0') + collect_data_files(dest_dir, 'dest')

# Add PyQt5 required modules to hiddenimports
hidden_imports = [
    'PyQt5.QtWidgets',
    'PyQt5.QtGui',
    'PyQt5.QtCore',
    # Add any other PyQt5 modules you use
]

a = Analysis(
    ['image_converter_gui.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ImageConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='C:\\Users\\fhe\\coding\\gitiiq\\IIQtoJPG\\logo.ico'  # Update this path
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='ImageConverter'
)
