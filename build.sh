#!/bin/bash
set -e # Exit on error

echo "Starting build process..."

# Verify required environment variables
echo "Verifying environment variables..."
required_vars=(
    "DB_HOST"
    "DB_PASSWORD"
    "SUPABASE_URL"
    "SUPABASE_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Setup Python environment
echo "Setting up Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found"
    exit 1
fi

echo "Python version:"
python3 --version

echo "Installing pip..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user

echo "Installing dependencies..."
python3 -m pip install --user --upgrade pip
python3 -m pip install --user -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p public
mkdir -p netlify/functions

# Copy static files and templates
echo "Copying static files..."
if [ -d "src/templates" ]; then
    cp -r src/templates/* public/ 2>/dev/null || true
fi

if [ -d "src/static" ]; then
    cp -r src/static/* public/ 2>/dev/null || true
fi

# Create a simple index.html that redirects to the Flask app
echo "Creating index.html..."
cat > public/index.html << EOL
<!DOCTYPE html>
<html>
<head>
    <title>SubMax</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
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
        window.location.href = '/admin/login';
    </script>
</body>
</html>
EOL

# Print environment information for debugging
echo "Environment information:"
echo "Python version: $(python3 --version)"
echo "Pip version: $(python3 -m pip --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

echo "Build completed successfully!" 