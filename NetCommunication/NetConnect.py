# -*- coding: UTF-8 -*-
import socket, struct

import NetThread
from CryptoAlgorithms import RsaKeyExchange, DiffieHellman
from GlobalData import CommonData, ConfigData, MagicNum


_metaclass_ = type
class NetConnect:
    def __init__(self,view):
        self.__Sockfd = socket.socket()
    
    def ChangeView(self,view):
        self.__view = view    
        
    def ReqConnect(self,name,psw):
        "请求登录"
        _msgbody = name + CommonData.MsgHandlec.PADDING + psw
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQLOGINMSG,len(_msgbody))
        self.__Sockfd.send(_msghead + _msgbody)
    
    def ReqRegister(self,name,psw):
        "请求注册"
        _rke = RsaKeyExchange.RsaKeyExchange()
        _rke.GenerateRsaKey()
        _pkeystr = _rke.GetPubkeyStr("own")
        print _pkeystr
        _msgbody = name + CommonData.MsgHandlec.PADDING + \
                   psw + CommonData.MsgHandlec.PADDING + \
                   _pkeystr
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQREGISTERMSG,len(_msgbody))
        self.__Sockfd.send(_msghead + _msgbody.decode('gbk').encode("utf-8"))
        
    def ReqFile(self,filename):
        "请求分发文件" 
        self.ThreadType = CommonData.ThreadType.CONNECTCP
        self.filename = filename
        _msgbody = filename.encode("utf-8")
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQOBTAINFILE, len(_msgbody))
        self.__Sockfd.send(_msghead + _msgbody)
        
        import wx
        from wx.lib.pubsub  import Publisher
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,"请求分发文件(" + _msgbody + ")")
    
    def ReqIdentify(self,username,filename):
        "发送文件名和内容提供商名，请求责任认定"
        self.ThreadType = CommonData.ThreadType.CONNECTAP
        self.auditusername = username
        self.auditfilename = filename
        #_msgbody = username + CommonData.MsgHandlec.PADDING + filename
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQIDENTIFIED, 0)
        self.__Sockfd.send(_msghead)
        
        import wx
        from wx.lib.pubsub  import Publisher
        showmsg = "请求对内容提供商(" + username + ")的文件(" + filename + ")进行责任认定"
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg)
    
    def ReqFileList(self):
        "请求文件列表"
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQFILELIST, 0)
        self.__Sockfd.send(_msghead)
        
    def StartNetConnect(self,address):
        "连接服务器并开启网络线程"
        try:
            import string
            print address
            self.__Sockfd.connect((address[0],string.atoi(address[1])))
        except Exception,e:
            print e
            return MagicNum.NetConnectc.NOTCONNECT
        self.__netThread = NetThread.NetThread(self.__Sockfd.dup(),self)
        self.__netThread.start()
        
    def StopNetConnect(self):
        "发送关闭消息并关闭网络线程"
        #self.__netThread.join()
        #放在主线程主执行
        pass
        
if __name__=='__main__':
    filename = "/home/keym/视频/小伙.mpg"
    _msgbody = filename[-filename[::-1].index("/"):].encode("utf-8")
    print "msgbody",_msgbody,len(_msgbody)