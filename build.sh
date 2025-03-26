#!/bin/bash

# Exit on any error
set -e

# Print debug information
echo "=== Debug Information ==="
pwd
ls -la
echo "Current directory contents:"
ls -R

echo "=== Starting build process ==="

# Print all environment variables (excluding sensitive data)
echo "=== Environment Variables ==="
env | grep -v 'PASSWORD\|KEY\|SECRET'

# Verify Python installation
echo "=== Verifying Python installation ==="
which python3 || which python3.9 || which python || true
python3 --version || python3.9 --version || python --version

# Create and activate virtual environment
echo "=== Setting up Python virtual environment ==="
python3.9 -m venv .venv
source .venv/bin/activate || source .venv/Scripts/activate

# Verify Python version
echo "=== Python Version ==="
python --version

# Install dependencies
echo "=== Installing dependencies ==="
python3 -m pip install --user --upgrade pip || python -m pip install --user --upgrade pip
python3 -m pip install --user -r requirements.txt || python -m pip install --user -r requirements.txt

# Create necessary directories
echo "=== Creating directories ==="
mkdir -p public
mkdir -p netlify/functions/app

# Setup Flask application for Netlify Functions
echo "=== Setting up Flask application ==="
cat > netlify/functions/app/index.py << EOL
from flask import Flask, request
from flask_cors import CORS
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from app import app as flask_app

# Enable CORS
CORS(flask_app)

# Handler for Netlify Functions
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': 'Flask app is running'
    }

# For local development
if __name__ == '__main__':
    flask_app.run()
EOL

# Copy application files
echo "=== Copying application files ==="
cp -r src/* netlify/functions/app/
cp requirements.txt netlify/functions/app/
cp runtime.txt netlify/functions/app/

# Create simple index.html
echo "=== Creating index.html ==="
cat > public/index.html << EOL
<!DOCTYPE html>
<html>
<head>
    <title>SubMax</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        body {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f8f9fa;
        }
        .loader {
            border: 4px solid #f3f3f3;
            border-radius: 50%;
            border-top: 4px solid #3498db;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="text-center">
        <div class="loader d-inline-block"></div>
        <p class="h4 d-inline-block">Loading SubMax...</p>
    </div>
    <script>
        setTimeout(function() {
            window.location.href = '/.netlify/functions/app';
        }, 1500);
    </script>
</body>
</html>
EOL

# Print directory structure for debugging
echo "=== Directory Structure ==="
ls -R || tree -L 3

echo "=== Build completed successfully ===" 