#!/usr/bin/env python
import sys
from bt.TorrentInspector import *


if __name__ == '__main__':
    info = open_torrent(sys.argv[1])
    print info
    print '----\n\t%s' % info.trackers
