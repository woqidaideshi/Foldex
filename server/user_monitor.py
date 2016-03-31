# -*- coding: utf-8 -*-

import logging
import time
import threading
from collections import defaultdict


log = logging.getLogger(__name__)


class UserMonitor(object):

    class Record(object):
        __slots__ = ['ip', 'vm', 'online', 'last_update']

    def __init__(self, timeout=30, interval=5):
        self.memo = defaultdict(self.Record)
        self.terminated = False
        self.refresher = threading.Thread(target=self.refresh_status)
        self.timeout = timeout
        self.refresh_interval = interval

    def __del__(self):
        self.stop()

    def update_connection(self, user, ip, vm=None):
        rec = self.memo[user]
        rec.ip = ip
        rec.vm = vm
        rec.online = True
        rec.last_update = time.time()

    def get_status(self, user):
        return self.memo[user]

    def refresh_status(self):
        while not self.terminated:
            now = time.time()
            log.debug('========== begin refresh ==========')
            for user in self.memo:
                rec = self.memo[user]
                if now - rec.last_update > self.timeout:
                    rec.online = False
                    log.debug('user {} offline'.format(user))
                    self.notify(user)
                else:
                    log.debug('user {} online'.format(user))
            log.debug('----------- end refresh -----------')
            time.sleep(self.refresh_interval)

    def notify(self, user):
        pass

    def start(self):
        self.terminated = False
        self.refresher.start()

    def stop(self):
        self.terminated = True
        self.refresher.join()

