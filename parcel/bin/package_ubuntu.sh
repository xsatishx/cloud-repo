#!/usr/bin/env bash

# Make sure the correct version of pyinstall is installed
pip install 'PyInstaller==2.1'

# Get version
VERSION=$(python -c 'import parcel; print parcel.__version__')

# Create binary
pyinstaller --clean --noconfirm --onefile -c parcel

APPNAME="Parcel"
SOURCE="dist/parcel"

# Zip dist
zip "parcel_${VERSION}_Ubuntu14.04_x64.zip" "${SOURCE}"
