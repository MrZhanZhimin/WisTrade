#!/bin/bash
# WisTrade Build Script for macOS/Linux

set -e

echo "Building WisTrade executable..."

# Check if PyInstaller is installed
if ! python -m pip show pyinstaller > /dev/null 2>&1; then
    echo "PyInstaller not found. Installing..."
    python -m pip install pyinstaller
fi

# Build the executable
echo ""
echo "Building executable..."
pyinstaller --clean wistrade.spec

echo ""
echo "Build complete!"
echo "Executable location: dist/WisTrade"
echo ""
