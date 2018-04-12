"""
This script runs the API1 application using a development server.
"""

from os import environ
from API import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5245'))
    except ValueError:
        PORT = 5245
    app.run(HOST, PORT, debug = True)
