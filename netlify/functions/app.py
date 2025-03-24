from app import app
from http.server import BaseHTTPRequestHandler
import json

def handler(event, context):
    """Handle incoming requests."""
    # Convert Netlify event to WSGI environment
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': '',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False
    }

    # Create response object
    response = {}
    status_code = 200
    headers = {}

    def start_response(status, response_headers):
        nonlocal status_code, headers
        status_code = int(status.split()[0])
        headers = dict(response_headers)

    # Get response from Flask app
    response_body = app(environ, start_response)

    # Convert response to Netlify format
    if isinstance(response_body, str):
        body = response_body
    else:
        body = b''.join(response_body).decode('utf-8')

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    } 