_metaclass_ = type

from MsgHandle import MsgHandleInterface
from GlobalData import MagicNum, ConfigData

class RecvFileBuffer(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvFileBuffer,self).__init__() 
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
        if session.currentbytes == 0:
            self.createMediaDir(session)
        recvbuffer = session.sockfd.recv(bufsize)
        session.currentbytes += len(recvbuffer)
        session.file.write(recvbuffer)
        msghead = self.packetMsg(MagicNum.MsgTypec.REQFILEBUFFER, 0)
        session.sockfd.send(msghead)