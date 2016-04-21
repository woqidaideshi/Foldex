#encoding=utf-8
import DBDao
import user_monitor
import session

class Handler(object):
    def __init__(self):
        self.processFuncs={
            "login":self.login,
            "logout":self.logout,
            "conn":self.connectVm,
            "disConn":self.disConnectVm,
            "heartBeat":self.heartBeat
        }
        self.mysqlConn=DBDao.Mysql()
        self.umt = user_monitor.UserMonitor()
        self.umt.start()
        self.sessons={}

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
            user = session.Session(msgObj['userName'], msgObj['password'])
            #self.sessions['user']=msgObj['userName']  本该这里记录当前用户连接信息 但是目前用户登录成功并连接vm后接受心跳
            vms=user.get_vms()
            result={};
            result['state']=1
            del msgObj['password']
            self.sessions[msgObj['userName']]=user
            self.umt.update_connection(msgObj['userName'],msgObj['ip'],None)
            result['user']=msgObj['userName']
            strategy=DBDao.get(self.mysqlConn,msgObj['userName'])
            result['strategy']=strategy
            result['vms']=vms
            return cb(result)
        except session.AuthenticationFailure as e:
            print e
            return cb({'state':0,'err':e})
        except session.VMError as e:
            print e
            return cb({'state':2,'err':e})
        except DBDao.MysqlError as e:
            print e
            return cb({'state':3,'err':e})
        except:
            print 'sth wrong when handle you msg'
            return cb({'err':'sth wrong when handle you msg'})
        

    def logout(self,msgObj,cb):
        print "logout"
        cb(msgObj)

    def connectVm(self,msgObj,cb):
        print "connectVm"
        try:
            #vm未开启时需要通知nova开启
            if msgObj['userName'] in self.sessions.keys():
                user=self.sessions['userName']
                # vms=self.sessions['userName']
                # for val in vms:
                #     if msgObj[vmId]==val['id']:
                #         if val['status']==0:
                # if msgObj['status']==0:#未开启
                    
                # else:
                user.start_vm(msgObj['id'])
                self.umt.update_connection(msgObj['userName'],msgObj['ip'],msgObj['id'])
                result={}
                result['state']=1
                cb(result)
            else:
                cb{'state':0,'err':'have no idea who are you'}
        except session.VMError as e:
            cb({'state':2,'err':e})
        except:
            cb({'state':2,'err':'sth wrong when handle you msg'})

    def disConnectVm(self,msgObj,cb):
        print "disConnectVm"
        #vm未开启时需要通知nova开启
        # if msgObj['userName'] in self.sessions.keys():
        #     self.umt.update_connection(msgObj['userName'],msgObj['ip'],None if 'id' not in msgObj.keys() else msgObj['id'])
        # cb({'state':1})
        cb(msgObj)

    def heartBeat(self,msgObj,cb):
        print "heartBeat"
        if msgObj['userName'] in self.sessions.keys():
            self.umt.update_connection(msgObj['userName'],msgObj['ip'],None if 'id' not in msgObj.keys() else msgObj['id'])
        cb({'state':1})


    def test(self):
        print "test"
