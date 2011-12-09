#!/usr/bin/env python
from BaseHTTPServer import (HTTPServer, BaseHTTPRequestHandler)
from bt import bencode
from urlparse import parse_qs

class Tracker(BaseHTTPRequestHandler):

    server_version = 'PyTracker/0.0001'

    def do_GET(self):
        start = self.path.index('?')+1
        rargs = self.path[start:]
        rargs = parse_qs(rargs, True)

        response = {}
        response['interval'] = 30000
        if hasattr(rargs, 'tracker_id'):
            response['tracker_id'] = self.tid
        response['complete'] = 0
        response['incomplete'] = 0
        response['peers'] = []
        for p in []:
            response['peers'].append(p.compact)

        response = bencode.bencode(response)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(response)
        return

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), Tracker)
    server.serve_forever()
