#!/bin/bash

echo "Starting the Flask app..."
gunicorn -b 0.0.0.0:5000 extract_text_api:app
