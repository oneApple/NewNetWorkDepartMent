# -*- coding: UTF-8 -*-
_metaclass_ = type
from MsgHandle import MsgHandleInterface
from GlobalData import CommonData

class RecvLoginSuccess(MsgHandleInterface.MsgHandleInterface,object):
    "登录成功转入主界面"
    def __init__(self):
        super(RecvLoginSuccess,self).__init__()
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = session.sockfd.recv(bufsize)                                                                                       
        recvlist = recvbuffer.split(CommonData.MsgHandlec.PADDING)
        self.sendViewMsg(CommonData.ViewPublisherc.LOGIN_SWITCH,recvlist)
        
