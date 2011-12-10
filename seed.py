#!/usr/bin/env python
from bt.TorrentInspector import open_torrent
import sys

if __name__ == '__main__':
    tor = open_torrent(sys.argv[1])
    while 1:
        continue
