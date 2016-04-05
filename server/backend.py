# -*- coding: utf-8 -*-

import logging
import session


log = logging.getLogger(__name__)


def login(username, password):
    log.info('User {} logging in'.format(username))
    try:
        user = session.Session(username, password)
        admin = session.AdminSession(username)
        info = admin.get_vms()
        info['token'] = user.token
        return info
    except session.AuthenticationFailure as e:
        log.error(e)
        raise


def request_connect(token, vm_id):
    user = session.Session.get(token)
    log.info('User {} attempt to connect to VM {}'.format(user.username, vm_id))
    try:
        user.start_vm(vm_id)
        return { vm_id: 'ACTIVE'}
    except VMError as e:
        log.error('User {} attempt to connect to {} but failed: {}'.format(user.username, vm_id, e))
        raise
