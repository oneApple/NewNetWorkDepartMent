# -*- coding: UTF-8 -*-

_metaclass_ = type

from MsgHandle import MsgHandleInterface
from GlobalData import MagicNum,ConfigData, CommonData

class RecvAllFile(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvAllFile,self).__init__() 
        _cfg = ConfigData.ConfigData()
        self.__mediapath = _cfg.GetMediaPath()
        
    def createMediaDir(self,session):
        import os 
        self.___ownPath = self.__mediapath + "/" + session.peername
        if not os.path.exists(self.___ownPath):
            if not os.path.exists(self.__mediapath):
                os.mkdir(self.__mediapath)
            os.mkdir(self.___ownPath)
        session.filename = session.control.filename
        _localfilename = self.___ownPath + "/" + session.filename
        session.file = open(_localfilename.encode('utf-8'),"wb")
    
    def HandleMsg(self,bufsize,session):
        "接收所有文件，请求A组参数"
        if session.currentbytes == 0:
            self.createMediaDir(session)
        recvbuffer = session.sockfd.recv(bufsize)
        session.file.write(recvbuffer)
        session.file.close()
        msghead = self.packetMsg(MagicNum.MsgTypec.REQAGROUP, 0)
        session.sockfd.send(msghead)
        
        showmsg = "文件接收完毕:\n(1)文件名:" + session.filename + "\n(2)文件大小:" + str(session.currentbytes + bufsize)
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_REWRITETEXT, CommonData.MsgHandlec.SPARATE + showmsg)
        session.currentbytes = 0
