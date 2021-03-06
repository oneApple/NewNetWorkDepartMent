# -*- coding: UTF-8 -*-
_metaclass_ = type
import string
from NetCommunication import NetSocketFun

from MsgHandle import MsgHandleInterface
from CryptoAlgorithms import DiffieHellman, Rsa
from GlobalData import CommonData, MagicNum, ConfigData

class RecvAndSendDh(MsgHandleInterface.MsgHandleInterface,object):
    "接受对方传来的dh参数p及公钥并生成自己的dh公钥，同时计算生成会话密钥,公钥"
    def __init__(self):
        super(RecvAndSendDh,self).__init__() 
    
    def verify(self,rsa,msg,sign,session):
        return  rsa.VerifyByPubkey(msg, sign, session.peername)
    
    def verifyMsgSign(self,msg,sign,session):
        "如果验证成功则发送公钥，否则发送验证失败并关闭该线程"
        _cfg = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfg.GetKeyPath())
        if self.verify(_rsa, msg[0], sign[0], session)== False or self.verify(_rsa, msg[1], sign[1], session)== False:
            msghead = self.packetMsg(MagicNum.MsgTypec.IDENTITYVERIFYFAILED, 0)
            NetSocketFun.NetSocketSend(session.sockfd, msghead )
            session.stop()
            showmsg = session.peername + "签名验证失败"
        else:
            #生成自己的会话密钥
            _dhkey = DiffieHellman.DiffieHellman(string.atol(msg[0]))
            from CryptoAlgorithms import HashBySha1
            _hbs = HashBySha1.HashBySha1()
            session.sessionkey = _hbs.GetHash(str(_dhkey.getKey(string.atol(msg[1]))),MagicNum.HashBySha1c.HEXADECIMAL)
            _dhpubkey = str(_dhkey.getPubkey())
            msglist = [_dhpubkey, _rsa.SignByPrikey(_dhpubkey)]
            msgbody = NetSocketFun.NetPackMsgBody(msglist)
            msghead = self.packetMsg(MagicNum.MsgTypec.SENDDHPUBKEY, len(msgbody))
            NetSocketFun.NetSocketSend(session.sockfd, msghead + msgbody ) 
            showmsg = "会话密钥:" + session.sessionkey
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg, True)
    
    def HandleMsg(self,bufsize,session):
        if session.control.ThreadType == CommonData.ThreadType.CONNECTAP:
            session.peername = "auditserver"
        "接受对方传来的dh参数及公钥并生成自己的dh公钥"
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        dhmsg = NetSocketFun.NetUnPackMsgBody(recvbuffer)
        #参数p：公钥：签名
        self.verifyMsgSign(dhmsg[:2], dhmsg[2:], session)
        