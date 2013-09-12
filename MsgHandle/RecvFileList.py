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
        table = []
        for index in range(len(_fileList) / 2):
            _singleFile = [_fileList[index * 2],_fileList[index * 2 + 1]]
            table.append(_singleFile)                                                                                      
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_REFRESHNETFILETABLE,table)
        
