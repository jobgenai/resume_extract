#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install LibreOffice (if not already installed)
if ! command -v libreoffice &> /dev/null
then
    echo "LibreOffice not found. Installing..."
    sudo apt-get update && sudo apt-get install -y libreoffice
else
    echo "LibreOffice is already installed."
fi

echo "Build process complete."
