# -*- coding: UTF-8 -*-
_metaclass_ = type
from wx.lib.pubsub  import Publisher
import wx

from MsgHandle import MsgHandleInterface
from GlobalData import CommonData

class RecvFileList(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvFileList,self).__init__()
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = session.sockfd.recv(bufsize)
        _fileList = recvbuffer.split(CommonData.MsgHandlec.PADDING)                                                                                       
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_SELECTFILE,_fileList)
        
