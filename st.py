#!/usr/bin/env python
from BaseHTTPServer import (HTTPServer, BaseHTTPRequestHandler)
import urlparse

class Tracker(BaseHTTPRequestHandler):

    server_version = 'PyTracker/0.0001'

    def do_GET(self):
        print self.headers
        self.send_response(200)
        self.end_headers()
        self.wfile.write('TBD')
        return

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), Tracker)
    server.serve_forever()
