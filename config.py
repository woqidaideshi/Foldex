# -*- coding: UTF-8 -*-
import sys,os
import ConfigParser

def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path) 

configPath=cur_file_dir()+'/config.ini'
cf = ConfigParser.ConfigParser()
cf.read(configPath)
HOST=cf.get("server", "host")
PORT = cf.getint("server", "port")
DBHOST=cf.get("mysql", "host")
DBPORT = cf.getint("mysql", "port")
USER = cf.get("mysql", "user")
PWD = cf.get("mysql", "password")
DB = cf.get("mysql", "db")
CHARSET = cf.get("mysql", "charset")
MINCACHED = int(cf.get("mysql", "mincached"))
MAXCACHED = int(cf.get("mysql", "maxcached"))
# cf.set("mysql", "db_pass", "123456")
# cf.write(open("config_file_path", "w"))