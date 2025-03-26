#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p public

# Copy static files
cp -r src/templates/* public/
cp -r src/static/* public/ 2>/dev/null || true

# Create a simple index.html that redirects to the Flask app
cat > public/index.html << EOL
<!DOCTYPE html>
<html>
<head>
    <title>SubMax</title>
    <meta http-equiv="refresh" content="0;url=/admin/login">
</head>
<body>
    <p>Redirecting to SubMax...</p>
</body>
</html>
EOL 