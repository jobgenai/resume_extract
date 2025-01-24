#!/bin/bash

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing LibreOffice..."
sudo apt-get update && sudo apt-get install -y libreoffice

echo "Build completed successfully."
