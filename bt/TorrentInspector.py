#!/usr/bin/env python
from StringIO import StringIO
import hashlib
import bencode
from Tracker import Tracker, TrackerRequest


PEER_ID = 'pytorrent123'*2

class NetAddress(list):
    def compact(self):
        a = struct.pack('>H', self._port())
        b = struct.pack('>4B', *self._ip())
        return ''.join([b, a])

    def ip(self):
        try:
            return '%d.%d.%d.%d' % self._ip()
        except TypeError:
            return None

    def port(self):
        return '%d' % self._port()

    def _ip(self):
        if len(self) == 2:
            return self[0]
        else:
            return None

    def _port(self):
        return self[-1]

def open_torrent(fn, port=6884, ip=None):
    try:
        fp = open(fn, 'rb')
        raw = fp.read()
    finally:
        fp.close()
    args = (ip, port)
    na = NetAddress(args)
    return TorrentFile(raw, na)

class BencDict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            pass

class InfoDict(BencDict):
    def __init__(self, d, e):
        self['plen'] = d['piece length']
        pieces = d['pieces']
        if e:
            pieces = pieces.decode(e)
        pieces = StringIO(pieces)
        self['pieces'] = [ piece for piece in pieces.read(20) ]
        self['dpieces'] = 0
        self['upieces'] = 0
        try:
            self['private'] = d['private']
        except KeyError:
            pass
        try:
            self['files'] = d['files']
            self['dir'] = d['name']
            self['len'] = (len(self['pieces']) * self['plen'])
        except KeyError:
            self['files'] = [ d['name'] ]
            self['len'] = d['length']
            try:
                self['md5'] = d['md5sum']
            except KeyError:
                pass
        self['started'] = False

    def sessionstats(self):
        total = (len(self['pieces']) * self['plen'])

        have = (self['dpieces']) * self['plen']

        left = total - have

        down = ((self['started'] == True) and [have] or [0])

        up = (len(self['pieces']) - self['upieces']) * self['plen']
        up = ((self['started'] == True) and [up] or [0])

        return (up[0], down[0], left)

    def __str__(self):
        try:
            file = self['files']
        except KeyError:
            file = self['dir']
        return file

class TorrentFile(object):
    def __init__(self, raw, ip):
        d = bencode.bdecode(raw)
        try:
            self.announce = [d['announce']]
        except KeyError:
            try:
                self.announce = [ l[0] for l in d['announce-list'] ]
            except KeyError:
                self.magnetinfo = d['magnet-info']
                self.announce = [self.magnetinfo['announce']]

        self.comment = getattr(d, 'comment', 'No Comment')
        self.creator = getattr(d, 'created by', 'Unknown')
        self.date = getattr(d, 'created on', None)
        self.encoding = getattr(d, 'encoding', None)
        info = d['info']
        sha = hashlib.sha1()
        sha.update(bencode.bencode(info))
        self.info_hash = sha.digest()
        print self.info_hash
        self.info = InfoDict(info, self.encoding)

        self.trackers = [ Tracker(TrackerRequest(na=ip, hash=self.info_hash, ID=PEER_ID, url=url, stats=self.info.sessionstats())) for url in self.announce ]

    def __str__(self):
        a = '%s torrent created by %s. %s. Announce: %s.'
        b = (self.info, self.creator, self.comment, self.announce)
        return a % b

