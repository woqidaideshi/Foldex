# -*- coding: utf-8 -*-

import json

class ConfigFile(object):
    def __init__(self, filename):
        with open(filename) as cf:
            self.conf = json.load(cf)

    def __getattr__(self, name):
        return self.conf[name]

cfg = ConfigFile(r'/etc/vds/vds.conf')
