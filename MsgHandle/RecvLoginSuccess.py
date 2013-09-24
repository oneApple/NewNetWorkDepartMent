# -*- coding: UTF-8 -*-
_metaclass_ = type
from MsgHandle import MsgHandleInterface
from NetCommunication import NetSocketFun
from GlobalData import CommonData

#from wx.lib.pubsub  import Publisher
#import wx

class RecvLoginSuccess(MsgHandleInterface.MsgHandleInterface,object):
    "登录成功转入主界面"
    def __init__(self):
        super(RecvLoginSuccess,self).__init__()
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        recvlist = NetSocketFun.NetUnPackMsgBody(recvbuffer)
        #wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.LOGIN_SWITCH,recvlist)
        self.sendViewMsg(CommonData.ViewPublisherc.LOGIN_SWITCH,recvlist)
        
