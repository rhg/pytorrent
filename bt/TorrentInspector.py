#!/usr/bin/env python
import bencode

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
    def __init__(self, d):
        self['len'] = d['piece length']
        self['num'] = d['pieces']
        try:
            self['private'] = d['private']
        except KeyError:
            pass
        try:
            self['files'] = d['files']
            self['dir'] = d['name']
        except KeyError:
            self['file'] = d['name']
            self['len'] = d['length']
            try:
                self['md5'] = d['md5sum']
            except KeyError:
                pass

    def __str__(self):
        try:
            file = self['file']
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
        self.info = InfoDict(d['info'])

    def __str__(self):
        a = '%s torrent created by %s. %s. Announce: %s.'
        b = (self.info, self.creator, self.comment, self.announce)
        return a % b

