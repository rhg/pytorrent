#!/usr/bin/env python
from StringIO import StringIO
import hashlib
import bencode
from Tracker import Tracker, TrackerRequest


PEER_ID = 'pytorrent123'*2

def open_torrent(fn):
    try:
        fp = open(fn, 'rb')
        raw = fp.read()
    finally:
        fp.close()
    return TorrentFile(raw)

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
        self['dpieces'] = list()
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

    def stats(self):
        tlen = 0
        for f in self['files']:
            with open(f, 'rb') as fn:
                flen = len(fn.read())
                tlen += flen
        left = self['len'] - tlen

        down = tlen

        up = self['dpieces'] * self['plen']

        return (up, down, left)

    def __str__(self):
        try:
            file = self['files']
        except KeyError:
            file = self['dir']
        return file

class TorrentFile(object):
    def __init__(self, raw):
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

        self.trackers = [ Tracker(TrackerRequest(port=9190, hash=self.info_hash, ID=PEER_ID, url=url, stats=self.info.stats())) for url in self.announce ]

    def __str__(self):
        a = '%s torrent created by %s. %s. Announce: %s.'
        b = (self.info, self.creator, self.comment, self.announce)
        return a % b

