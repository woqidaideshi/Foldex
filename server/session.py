import openstack
from openstack import connection

class AuthenticationFailure:
    def __str__(self):
        return "Authentication failed."

class Session(object):
    def __init__(self, username, password):
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
        def get_floating_ips(networks):
            result = []
            for name in networks:
                for address in networks[name]:
                    if address['OS-EXT-IPS:type'] == 'floating':
                        result.append(address['addr'])
            return result

        instances = self.conn.compute.servers()
        return [{u'id': vm.id, u'status': vm.status, u'ips': get_floating_ips(vm.addresses)} for vm in instances]

    def start_vm(self, vm_id):
        session = self.conn.session
        vm = self.conn.compute.get_server(vm_id)
        if vm.status == 'SHUTOFF':
            body = {'os-start': ''}
            vm.action(session, body)

def test():
    session = Session('user1', '123456')
    vms = session.get_vms()
    for vm in vms:
        print(vm)
        session.start_vm(vm['id'])


if __name__ == '__main__':
    test()
