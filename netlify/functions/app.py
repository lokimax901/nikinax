import sys
import os
from pathlib import Path

# Add the public directory to Python path
current_dir = Path(__file__).resolve().parent
public_dir = current_dir.parent.parent / 'public'
sys.path.append(str(public_dir))

from app import app

def handler(event, context):
    """Handle incoming requests."""
    # Parse request
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_string = event.get('queryStringParameters', {})
    body = event.get('body', '')

    # Convert Netlify event to WSGI environment
    environ = {
        'REQUEST_METHOD': http_method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join(f"{k}={v}" for k, v in query_string.items()) if query_string else '',
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': headers.get('content-length', ''),
        'SERVER_NAME': 'netlify',
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': body.encode('utf-8'),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add HTTP headers
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value

    # Create response object
    response = {}
    def start_response(status, response_headers, exc_info=None):
        status_code = int(status.split()[0])
        response['statusCode'] = status_code
        response['headers'] = dict(response_headers)

    # Get response from Flask app
    response_body = app(environ, start_response)
    
    # Convert response body to string
    if isinstance(response_body, (list, tuple)):
        response_body = b''.join(response_body)
    if isinstance(response_body, bytes):
        response_body = response_body.decode('utf-8')
    
    response['body'] = response_body
    return response 