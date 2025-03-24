import sys
import os
from pathlib import Path
import logging
import traceback
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('netlify_function')

# Add the public directory to Python path
current_dir = Path(__file__).resolve().parent
public_dir = current_dir.parent.parent / 'public'
sys.path.append(str(public_dir))

logger.info(f"Current directory: {current_dir}")
logger.info(f"Public directory: {public_dir}")
logger.info(f"Python path: {sys.path}")

try:
    from app import app
    logger.info("Successfully imported Flask app")
except Exception as e:
    logger.error(f"Failed to import Flask app: {str(e)}")
    logger.error(traceback.format_exc())
    raise

def handler(event, context):
    """Handle incoming requests."""
    try:
        # Log the full event for debugging
        logger.info("Received new request")
        logger.debug(f"Full event: {json.dumps(event, indent=2)}")
        
        # Parse request
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        query_string = event.get('queryStringParameters', {})
        body = event.get('body', '')

        logger.info(f"Processing {http_method} request to {path}")
        logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
        logger.debug(f"Query parameters: {json.dumps(query_string, indent=2)}")
        
        if body:
            logger.debug(f"Request body: {body[:200]}...")  # Log first 200 chars of body

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
            'wsgi.input': body.encode('utf-8') if body else b'',
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'HTTP_HOST': headers.get('host', ''),
            'HTTP_USER_AGENT': headers.get('user-agent', ''),
            'HTTP_ACCEPT': headers.get('accept', ''),
        }

        # Add HTTP headers
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value

        logger.debug(f"Created WSGI environment: {json.dumps(environ, indent=2)}")

        # Create response object
        response = {}
        def start_response(status, response_headers, exc_info=None):
            status_code = int(status.split()[0])
            response['statusCode'] = status_code
            response['headers'] = dict(response_headers)
            logger.info(f"Response status: {status}")
            logger.debug(f"Response headers: {json.dumps(dict(response_headers), indent=2)}")

        # Get response from Flask app
        logger.info("Calling Flask application")
        response_body = app(environ, start_response)
        
        # Convert response body to string
        if isinstance(response_body, (list, tuple)):
            response_body = b''.join(response_body)
        if isinstance(response_body, bytes):
            response_body = response_body.decode('utf-8')
        
        response['body'] = response_body
        logger.info(f"Response generated successfully, body length: {len(response_body)}")
        logger.debug(f"Response body preview: {response_body[:200]}...")  # Log first 200 chars
        
        return response

    except Exception as e:
        logger.error("Error handling request")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        } 