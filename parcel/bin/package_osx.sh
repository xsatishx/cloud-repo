#!/usr/bin/env bash

# Make sure the correct version of pyinstall is installed
pip install 'PyInstaller==2.1'

# Get version
VERSION=$(python -c 'import parcel; print parcel.__version__')

# Create binary
pyinstaller --clean --noconfirm --onefile -c  parcel

# Bundle app
APPNAME="Parcel"

BUNDLE="dist/${APPNAME}.app"
SOURCE="dist/parcel"
ICON="../resources/parcel.icns"
CONTENTS="${BUNDLE}/Contents"
MacOS="${CONTENTS}/MacOS"
RESOURCES="${CONTENTS}/Resources"
WRAPPER="${MacOS}/${APPNAME}"

if [ -a "${BUNDLE}" ]; then
    rm -rf "${BUNDLE}"
fi

echo "Bundling to ${BUNDLE}"

# Create bundle
mkdir -p "${MacOS}"

# Create wrapper script
echo '#!/bin/bash
BIN="$(cd "$(dirname "$0")"; pwd)/.parcel"
chmod +x "${BIN}"
open -a Terminal "${BIN}"
' > "${WRAPPER}"
chmod +x "${WRAPPER}"

# Move binary into bundle
cp "${SOURCE}" "${MacOS}/.${APPNAME}"

# Add icon
mkdir "${RESOURCES}"
cp "${ICON}" "${RESOURCES}/"
echo '
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist SYSTEM
"file://localhost/System/Library/DTDs/PropertyList.dtd">
<plist version="0.9">
<dict>
   <key>CFBundleIconFile</key>
   <string>parcel.icns</string>
</dict>
</plist>
' > "${CONTENTS}/Info.plist"

# Zip dist
zip "parcel_${VERSION}_OSX_x64.zip" "${BUNDLE}" "${SOURCE}"
