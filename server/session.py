# -*- coding: utf-8 -*-

import logging
import re
import time
import socket
import subprocess

import openstack

from openstack import connection

log = logging.getLogger(__name__)

class AuthenticationFailure:
    """认证异常"""

    def __init__(self, user):
        self.user = user

    def __str__(self):
        return "Authentication failed: {}".format(self.user)


class VMError:
    """VM状态异常"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Session(object):
    """用户会话类，以用户的身份执行操作。"""

    # 状态轮询间隔
    status_check_interval = 0.5
    # 等待状态超时时间
    status_wait_timeout = 10
    # spice 端口号匹配样式
    spice_port_pattern = re.compile(r'-spice port=(?P<port>\d+),')

    def __init__(self, username, password, project=None):
        """使用用户名和密码创建会话。

        默认每个用户拥有独立的同名项目，也可以指定项目名称。
        自动进行身份验证，验证失败时抛出异常。
        """
        self.conn = connection.Connection(auth_url="http://localhost:5000/v3",
                project_name=username if project is None else project,
                username=username,
                password=password,
                user_domain_id='Default',
                project_domain_id='Default')
        try:
            self.token = self.conn.authorize()
        except openstack.exceptions.HttpException:
            raise AuthenticationFailure(username)

    def get_vms(self):
        """获取用户项目中的所有VM。

        返回每个VM的id，状态和浮动ip。
        """
        def get_floating_ips(networks):
            """从网络信息中提取浮动ip。"""
            result = []
            for name in networks:
                for address in networks[name]:
                    if address['OS-EXT-IPS:type'] == 'floating':
                        result.append(address['addr'])
            return result

        def get_spice_port(vm_id):
            ps = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
            qemu = subprocess.Popen(["grep", vm_id], stdin=ps.stdout, stdout=subprocess.PIPE)
            out = qemu.communicate()[0]
            m = self.spice_port_pattern.search(out)
            return m.group('port') if m else ''

        instances = self.conn.compute.servers() # instances 是 generator
        return [{u'id': vm.id,
                 u'status': vm.status,
                 u'floating_ips': get_floating_ips(vm.addresses),
                 u'spice_port': get_spice_port(vm.id)} for vm in instances]


    def wait_for_status(self, vm_id, status, timeout):
        """等待指定VM达到需要的状态。

        如果VM处于错误状态或超时则抛出异常。
        status: 可能的值为 ACTIVE, BUILDING, DELETED, ERROR, HARD_REBOOT, PASSWORD,
                PAUSED, REBOOT, REBUILD, RESCUED, RESIZED, REVERT_RESIZE, SHUTOFF,
                SOFT_DELETED, STOPPED, SUSPENDED, UNKNOWN, VERIFY_RESIZE
        timeout: 超时时限，秒
        """
        now = time.time()
        deadline = now + timeout
        while now < deadline:
            vm = self.conn.compute.get_server(vm_id)
            if vm.status == status:
                break
            if vm.status == 'ERROR':
                raise VMError('VM is in error state.')
            time.sleep(self.status_check_interval)
            now = time.time()
        else:
            raise VMError('Action timeout.')

    def start_vm(self, vm_id):
        """启动用户的VM。

        返回时VM已启动，或因错误无法启动，或操作超时。
        后两者抛出VMError异常。
        """
        session = self.conn.session
        vm = self.conn.compute.get_server(vm_id)
        if vm.status == 'SHUTOFF': # 只在关机状态下执行
            log.info('Starting VM {}'.format(vm_id))
            body = {'os-start': ''}
            vm.action(session, body)
            self.wait_for_status(vm, 'ACTIVE', self.status_wait_timeout)

    def stop_vm(self, vm_id):
        """关闭用户的VM。

        返回时VM已关闭，或因错误无法关闭，或操作超时。
        后两者抛出VMError异常。
        """
        session = self.conn.session
        vm = self.conn.compute.get_server(vm_id)
        if vm.status == 'ACTIVE': # 只在开机状态下执行
            log.info('Shuting down VM {}'.format(vm_id))
            body = {'os-stop': ''}
            vm.action(session, body)
            self.wait_for_status(vm, 'SHUTOFF', self.status_wait_timeout)


class AdminSession(Session):
    def __init__(self, project):
        admin_user = 'admin' # TODO: 从配置中读取
        admin_pass = '2e85593e07a34568'
        super(AdminSession, self).__init__(admin_user, admin_pass, project=project)

    def get_vm_host(self, vm_id):
        vm = self.conn.compute.get_server(vm_id)
        host = vm['OS-EXT-SRV-ATTR:hypervisor_hostname']
        return host, socket.gethostbyname(host)

    def get_vms(self):
        vms = super(AdminSession, self).get_vms()
        for vm in vms:
            hostname, host_ip = self.get_vm_host(vm['id'])
            vm[u'host_name'] = hostname
            vm[u'host_ip'] = host_ip
        return vms


def test():
    user = Session('user1', '123456')
    admin = AdminSession('user1')
    vms = admin.get_vms()
    for vm in vms:
        log.debug(vm)

    #    try:
    #        session.stop_vm(vm['id'])
    #        log.info('VM powered off.')
    #        session.start_vm(vm['id'])
    #        log.info('VM powered on.')
    #    except VMError as e:
    #        log.error(e)


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]\t%(name)s | %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    test()
