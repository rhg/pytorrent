#!/usr/bin/env python
# coding=utf-8
from BaseHTTPServer import (HTTPServer, BaseHTTPRequestHandler)
from bt import bencode
from urlparse import parse_qs
import struct
import re


torrents = { ";ÛüÂ0Ì‰Íà'±stª/Ë":[0, 0, []] }

class InvalidRequest(ValueError):
    pass

class Peer(tuple):
    def __new__(cls, ip, host):
        ipm = re.match(r'(\d{0,3}).(\d{0,3}).(\d{0,3}).(\d{0,3})', ip)
        ip = tuple(int(e) for e in ipm.groups())
        host = int(host)
        return super(Peer, cls).__new__(cls, (ip, host))

    def compact(self):
        return struct.pack('>H4B', self[1], *self[0])

class Tracker(BaseHTTPRequestHandler):

    server_version = 'PyTracker/0.0002'

    def do_GET(self):
        tid = 'Anon\'s Test Tracker'
        start = self.path.index('?')+1
        rargs = self.path[start:]
        rargs = parse_qs(rargs, True)
        rargs = { k:v[0] for k, v in rargs.items() }
        print rargs
        info_hash = rargs['info_hash']
        if int(rargs['left']) == 0:
            torrents[info_hash][0] += 1
        elif int(rargs['left']) > 0:
            torrents[info_hash][1] += 1
        else:
            raise InvalidRequest('What\'s left?')
        if not hasattr(rargs, 'ip'):
            rargs['ip'] = self.client_address[0]
        npeer = Peer(rargs['ip'], rargs['port'])
        torrents[info_hash][2].append(npeer)

        response = {}
        response['interval'] = 30000
        if not hasattr(rargs, 'tracker_id'):
            response['tracker_id'] = tid
        response['complete'] = torrents[info_hash][0]
        response['incomplete'] = torrents[info_hash][1]
        response['peers'] = [ p.compact() for p in torrents[info_hash][2] ]

        print response
        response = bencode.bencode(response)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(response)
        return

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), Tracker)
    server.serve_forever()

