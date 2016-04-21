#encoding=utf-8
import BaseHTTPServer
import json
import serverRequestHandler

from oslo_config import cfg

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
        print "get------------"
        datas = self.rfile.read(int(self.headers['content-length']))
        # print datas
        # print self.client_address
        # print self.path
        # print self.command
        dataObj=json.loads(datas)
        dataObj['ip']=self.client_address
        serverRequestHandler.processMsg(self.path[1:],dataObj,self.sendResult)


    def do_POST( self ):
        print "post----------"
        datas = self.rfile.read(int(self.headers['content-length']))
        dataObj=json.loads(datas)
        dataObj['ip']=self.client_address
        serverRequestHandler.processMsg(self.path[1:],dataObj,self.sendResult)

    def sendResult(self,msg):
        print 'result:',msg
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

if __name__=='__main__':

    cfg.CONF(default_config_files=['../etc/foldex.conf'])
    HOST,PORT=CONF.server.host,CONF.server.port
    serverRequestHandler=serverRequestHandler.Handler()
    # handler = http.server.SimpleHTTPRequestHandler
    
    try:
        server=BaseHTTPServer.HTTPServer((HOST,PORT),RequestHandler)
        print("server at port ",PORT)
        server.serve_forever()
    except :
        print "sth wrong"
