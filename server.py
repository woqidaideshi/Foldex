#encoding=utf-8
import BaseHTTPServer
import json
import serverRequestHandler
import config

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET( self ):
        print "get------------"
        datas = self.rfile.read(int(self.headers['content-length']))
        # print datas
        # print self.client_address
        # print self.path
        # print self.command
        serverRequestHandler.processMsg(self.path[1:],json.loads(datas),self.sendResult)


    def do_POST( self ):
        print "post----------"
        datas = self.rfile.read(int(self.headers['content-length']))
        serverRequestHandler.processMsg(self.path[1:],json.loads(datas),self.sendResult)

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

    HOST,PORT=config.HOST,config.PORT
    serverRequestHandler=serverRequestHandler.Handler()
    # handler = http.server.SimpleHTTPRequestHandler
    try:
        server=BaseHTTPServer.HTTPServer((HOST,PORT),RequestHandler)
        print("server at port ",PORT)
        server.serve_forever()
    except :
        print "sth wrong"