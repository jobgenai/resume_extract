#!/bin/bash

# Set environment variables
export FLASK_APP=extract_text_api.py
export FLASK_ENV=production

# Ensure the custom temp directory exists
mkdir -p ~/my_temp_files

# Start the Flask app
echo "Starting the Flask server..."
flask run --host=0.0.0.0 --port=5000
