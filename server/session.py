import openstack
from openstack import connection

class AuthenticationFailure:
    """认证异常"""
    
    def __str__(self):
        return "Authentication failed."

class Session(object):
    """用户会话类，以用户的身份执行操作。
    
    默认每个用户拥有独立的同名项目。
    """
    
    def __init__(self, username, password):
        """使用用户名和密码创建会话。
        
        自动进行身份验证，验证失败时抛出异常。
        """
        self.conn = connection.Connection(auth_url="http://localhost:5000/v3",
                project_name=username,
                username=username,
                password=password,
                user_domain_id='Default',
                project_domain_id='Default')
        try:
            self.token = self.conn.authorize()
        except openstack.exceptions.HttpException:
            raise AuthenticationFailure


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

        instances = self.conn.compute.servers()
        return [{u'id': vm.id, u'status': vm.status, u'ips': get_floating_ips(vm.addresses)} for vm in instances]

    def start_vm(self, vm_id):
        """启动用户的VM。"""
        session = self.conn.session
        vm = self.conn.compute.get_server(vm_id)
        if vm.status == 'SHUTOFF': # 只在关机状态下执行
            body = {'os-start': ''}
            vm.action(session, body)
            # TODO: 确认启动完成后返回

def test():
    session = Session('user1', '123456')
    vms = session.get_vms()
    for vm in vms:
        print(vm)
        session.start_vm(vm['id'])


if __name__ == '__main__':
    test()
