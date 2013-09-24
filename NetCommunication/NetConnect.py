# -*- coding: UTF-8 -*-
import socket, struct

import NetThread
from CryptoAlgorithms import RsaKeyExchange, DiffieHellman
from GlobalData import CommonData, ConfigData, MagicNum
from NetCommunication import NetSocketFun

_metaclass_ = type
class NetConnect:
    def __init__(self,view):
        self.__Sockfd = socket.socket()
    
    def ChangeView(self,view):
        self.__view = view    
        
    def ReqConnect(self,name,psw):
        "请求登录"
        msglist = name + [psw]
        _msgbody = NetSocketFun.NetPackMsgBody(msglist)
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQLOGINMSG,len(_msgbody))
        NetSocketFun.NetSocketSend(self.__Sockfd,_msghead + _msgbody)
    
    def ReqRegister(self,name,psw):
        "请求注册"
        _rke = RsaKeyExchange.RsaKeyExchange()
        _rke.GenerateRsaKey()
        _pkeystr = _rke.GetPubkeyStr("own")
        msglist = [name,psw,_pkeystr]
        _msgbody = NetSocketFun.NetPackMsgBody(msglist)
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQREGISTERMSG,len(_msgbody))
        NetSocketFun.NetSocketSend(self.__Sockfd,_msghead + _msgbody.decode('gbk').encode("utf-8"))
        
    def ReqFile(self,filename,username):
        "请求分发文件" 
        self.ThreadType = CommonData.ThreadType.CONNECTCP
        self.filename = filename
        msglist = [filename.encode("utf-8"),username.encode("utf-8")]
        _msgbody = NetSocketFun.NetPackMsgBody(msglist).encode("utf-8")
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQOBTAINFILE, len(_msgbody))
        NetSocketFun.NetSocketSend(self.__Sockfd,_msghead + _msgbody)
        
        import wx
        from wx.lib.pubsub  import Publisher
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,["请求分发文件(" + filename + ")", False])
    
    def ReqIdentify(self,username,filename):
        "发送文件名和内容提供商名，请求责任认定"
        self.ThreadType = CommonData.ThreadType.CONNECTAP
        self.auditusername = username
        self.auditfilename = filename
        #_msgbody = username + CommonData.MsgHandlec.PADDING + filename
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQIDENTIFIED, 0)
        NetSocketFun.NetSocketSend(self.__Sockfd,_msghead)
        
        import wx
        from wx.lib.pubsub  import Publisher
        showmsg = "请求对内容提供商(" + username + ")的文件(" + filename + ")进行责任认定"
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,[showmsg, False])
    
    def ReqFileList(self):
        "请求文件列表"
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQFILELIST, 0)
        NetSocketFun.NetSocketSend(self.__Sockfd,_msghead)
        
    def StartNetConnect(self,address,peername = "auditserver"):
        "连接服务器并开启网络线程"
        try:
            import string
            self.__Sockfd.connect((address[0],string.atoi(address[1])))
        except Exception,e:
            import wx
            return MagicNum.NetConnectc.NOTCONNECT
        self.__netThread = NetThread.NetThread(self.__Sockfd.dup(),self,peername)
        self.__netThread.start()
        
    def StopNetConnect(self):
        "发送关闭消息并关闭网络线程"
        _msghead = struct.pack(CommonData.MsgHandlec.MSGHEADTYPE,MagicNum.MsgTypec.REQCLOSEMSG, 0)
        NetSocketFun.NetSocketSend(self.__Sockfd,_msghead)
        self.__netThread.stop()
        #放在主线程主执行
        
if __name__=='__main__':
    filename = "/home/keym/视频/小伙.mpg"
    _msgbody = filename[-filename[::-1].index("/"):].encode("utf-8")
