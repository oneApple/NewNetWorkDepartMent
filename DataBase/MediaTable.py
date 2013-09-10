# -*- coding: UTF-8 -*-
import sqlite3

from DataBase import DataBaseInterface
from GlobalData import MagicNum

class MediaTable(DataBaseInterface.DataBaseInterface,object):
    def __init__(self):
        "初始化父类"
        super(MediaTable,self).__init__()
    
    def CreateTable(self):
        "创建媒体表"
        self.ExcuteCmd("CREATE TABLE MediaTable (medianame TEXT, username TEXT, signParam TEXT, sign TEXT, signHash TEXT, status INT,PRIMARY KEY(medianame,username))")
    
    def AddNewMedia(self,value):
        "增加新的媒体"
        value += [MagicNum.MediaTablec.ACCEPT]
        try:
            self.InsertValue("MediaTable",value)
        except sqlite3.IntegrityError:
            return False
        return True
    
    def AlterMedia(self,attri,value,medianame,username):
        "更改媒体表"
        _sql = "UPDATE MediaTable SET "+ attri +"=? where medianame=? and username=?"
        self.ExcuteCmd(_sql,[value,medianame,username])
    
    def searchMedia(self,medianame,username):
        _sql = "SELECT * FROM MediaTable where medianame=? and username=?"
        return self.Search(_sql, [medianame,username])
    
    def deleteMedia(self,medianame,username):
        _sql = "DELETE FROM MediaTable WHERE medianame=? and username=?"
        self.ExcuteCmd(_sql, [medianame,username])  
    
    def deleteTable(self):
        _sql = "DROP TABLE MediaTable"
        self.ExcuteCmd(_sql)  
    
if __name__=='__main__':
    a = MediaTable()
    a.Connect()
    #a.deleteTable()
    #a.CreateTable()
    #a.AddNewMedia(["a","cp","signParam","sign","signHash"])
    #a.deleteMedia("shiyan.mpg","cp")
