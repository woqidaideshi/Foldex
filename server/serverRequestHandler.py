#encoding=utf-8
import DBDao

class Handler(object):
    def __init__(self):
        print 'serverRequestHandler'
        self.processFuncs={
            "login":self.login,
            "logout":self.logout,
            "conn":self.connectVm,
            "disConn":self.disConnectVm,
            "heartBeat":self.heartBeat
        }
        self.sessions={}
        self.dbDao=DBDao.Mysql()

    def processMsg(self,action,msgObj,cb):
        try:
            return self.processFuncs.get(action)(msgObj,cb)
        except :
            print "unknown action"
            return cb({'err':'unknown action'})

    def login(self,msgObj,cb):
        print "login"
        try:
            pass
            #请求keystone获得身份认证结果
            #认证通过请求vm信息
            #得到vm获取本地策略
            #返回认证结果+vm信息+本地策略
            #本地sessions更新接收heartBeat
            return cb(msgObj)
        except:
            print 'sth wrong when handle you msg'
            return cb({'err':'sth wrong when handle you msg'})
        

    def logout(self,msgObj,cb):
        print "logout"
        cb(msgObj)

    def connectVm(self,msgObj,cb):
        print "connectVm"
        #vm未开启时需要通知nova开启
        cb(msgObj)

    def disConnectVm(self,msgObj,cb):
        print "disConnectVm"
        #vm未开启时需要通知nova开启
        cb(msgObj)

    def heartBeat(self,msgObj,cb):
        print "heartBeat"
        cb(msgObj)


    def test(self):
        print "test"
