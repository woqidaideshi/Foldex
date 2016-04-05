#encoding=utf-8
import BaseHTTPServer
import json
import serverRequestHandler
import logconf

from oslo_config import cfg


logging.config.dictConfig(logconf.conf_dict)
log = logging.getLogger('server.server')


opt_server_group = cfg.OptGroup(name='server',
                            title='Foldex Server IP Port')

server_opts = [
    cfg.StrOpt('host', default='127.0.0.1',
               help=('Host IP')),
    cfg.IntOpt('port', default=8893,
               help=('Host Port')),
]

CONF = cfg.CONF
CONF.register_group(opt_server_group)
CONF.register_opts(server_opts, opt_server_group)

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET( self ):
        log.debug("get------------")
        datas = self.rfile.read(int(self.headers['content-length']))
        # print datas
        # print self.client_address
        # print self.path
        # print self.command
        serverRequestHandler.processMsg(self.path[1:],json.loads(datas),self.sendResult)


    def do_POST( self ):
        log.debug("post----------")
        datas = self.rfile.read(int(self.headers['content-length']))
        serverRequestHandler.processMsg(self.path[1:],json.loads(datas),self.sendResult)

    def sendResult(self,msg):
        log.debug('result:',msg)
        if msg.has_key('err'):
            self.send_response( 500 )
        else:
            self.send_response( 200 )
        self.send_header("Content-type", "text/html;charset=utf-8" )
        # f = open('C:/workspaces/workspace_python/client/client.py','r')
        # ct = f.read()
        msg=json.dumps(msg)
        self.send_header('Content-length', str(len(msg)))
        self.end_headers()
        self.wfile.write( msg )
        print 'ok'


def main():
    cfg.CONF(default_config_files=['/etc/foldex/foldex.conf'])
    host, port = CONF.server.host, CONF.server.port
    serverRequestHandler = serverRequestHandler.Handler()
    # handler = http.server.SimpleHTTPRequestHandler
    
    try:
        server = BaseHTTPServer.HTTPServer((host, port), RequestHandler)
        log.debug("Serving at port {}".format(port))
        server.serve_forever()
    except :
        log.debug("Failed to start server")


if __name__ == '__main__':
    main()
