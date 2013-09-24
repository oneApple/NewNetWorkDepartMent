# -*- coding: UTF-8 -*-
_metaclass_ = type
from wx.lib.pubsub  import Publisher
from NetCommunication import NetSocketFun
import wx

from MsgHandle import MsgHandleInterface
from GlobalData import CommonData

class RecvFileList(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvFileList,self).__init__()
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        _fileList = NetSocketFun.NetUnPackMsgBody(recvbuffer) 
        table = []
        for index in range(len(_fileList)):
            _singleFile = NetSocketFun.NetUnPackMsgBody(_fileList[index])
            table.append(_singleFile)                                                                                      
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_REFRESHNETFILETABLE,table)
        
