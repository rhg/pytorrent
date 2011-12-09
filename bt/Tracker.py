#!/usr/bin/env python
import urllib
import urllib2


class TrackerRequest(list):
    def __init__(self, **args):
        self.url = args['url']
        self.info_hash = args['hash']
        self.peer_id = args['ID']
        self.settings = args['stats']
        #self.ip = args['ip']

class Tracker(object):
    '''An abstraction af a tracker.
    uses urllib to send GET requests with a custom UA.
    Uses values from a TorrentRequest object and that is the only paramater'''
    def __init__(self, tf):
        '''def __init__(self,tf):
        tf = a TorrentFile object'''
        self.url = tf.url
        self.params = [
            ('info_hash', tf.info_hash),
            ('peer_id', tf.peer_id),
            #('port', tf.settings['port']),
            ('compact', 1)
            #('ip', tf.ip),
            ]
        initial = self._update_vars(tf, 'start')
        url = '%s?%s' % (tf.url, urllib.urlencode(initial))
        req = urllib2.Request(url)
        req.add_header('User-agent', 'pytorrent 0.0001 (www.github.com/rhg/pytorrent')
        res = urllib2.urlopen(req)
        data = res.read()
        print data

    def _update_vars(self, tf, event=''):
        new = list(self.params)
        new.extend([('uploaded', tf.settings[0]), ('downloaded', tf.settings[1]),
            ('left', tf.settings[2]), ('event', event)])
        return new
