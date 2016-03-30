#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import sys, os.path as path 
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from server import session


log_conf_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s | %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': logging.DEBUG,
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'server': {
            'level': logging.DEBUG,
            'handlers': ['console']
        }
    }
}

logging.config.dictConfig(log_conf_dict)
log = logging.getLogger('server.test_os')


def test():
    user = session.Session('user1', '123456')
    admin = session.AdminSession('user1')
    vms = admin.get_vms()
    for vm in vms:
        log.debug(vm)

        try:
            user.stop_vm(vm['id'])
            user.start_vm(vm['id'])
        except session.VMError as e:
            log.error(e)


if __name__ == '__main__':
    test()
