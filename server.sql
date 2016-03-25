drop database if exists foldexserver;
create database foldexserver default character set utf8;

CREATE TABLE foldexserver.user(id INT PRIMARY KEY auto_increment, userName varchar(32), strategy varchar(256),unique(userName)) default charset=utf8;
INSERT INTO foldexserver.user ( userName, strategy )VALUES('admin','');
INSERT INTO foldexserver.user ( userName, strategy )VALUES('user','');
INSERT INTO foldexserver.user ( userName, strategy )VALUES('user2','');