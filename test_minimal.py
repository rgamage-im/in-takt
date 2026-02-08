"""
Minimal WSGI application to test if Azure routing works at all.
This bypasses ALL Django functionality.
"""

def application(environ, start_response):
    """Absolute minimum WSGI app"""
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Hello from Azure - minimal WSGI test']
