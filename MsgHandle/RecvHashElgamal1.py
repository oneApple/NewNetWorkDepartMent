#coding=utf-8
_metaclass_ = type
from NetCommunication import NetSocketFun

from MsgHandle import MsgHandleInterface
from GlobalData import CommonData, MagicNum, ConfigData
from CryptoAlgorithms import Rsa, Elgamal

class RecvHashElgamal1(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvHashElgamal1,self).__init__()
    
    def handleRecvMsg(self,msgList,session):
        "获取对方传来的elgamal"
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        if _rsa.DecryptByPrikey(msgList[0]) == session.sessionkey:
            import struct
            session.elgamal2list = []
            for index in range(1,len(msgList),2):
                elgamal1 = struct.unpack(msgList[index],msgList[index + 1])
                elgamal2 = session.elgamal.EncryptoList(elgamal1)
                session.elgamal2list.append(Elgamal.GetStructFmt(elgamal2))
                session.elgamal2list.append("".join(elgamal2))
            return True
        else:
            return False  
    
    def getCipherText(self,session):
        "对参数和会话密钥进行加密"
        _cfg = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfg.GetKeyPath())
        plaintext = session.sessionkey
        return _rsa.EncryptByPubkey(plaintext, session.peername)
    
    def packSendMsgBody(self,session):
        elgamallist = session.elgamal2list
        showmsg = "二次加密Ａ组比特串承诺"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg, True)
        return [repr(self.getCipherText(session))] + elgamallist
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        _msglist = NetSocketFun.NetUnPackMsgBody(recvbuffer)
        if self.handleRecvMsg(_msglist, session) == True:
            msglist = self.packSendMsgBody(session)
            msgbody = NetSocketFun.NetPackMsgBody(msglist)
            msghead = self.packetMsg(MagicNum.MsgTypec.SENDHASHELGAMAL2, len(msgbody))
            NetSocketFun.NetSocketSend(session.sockfd,msghead + msgbody)
            return
        else:
            showmsg = "签名验证失败,发送方为恶意用户"
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
        msghead = self.packetMsg(MagicNum.MsgTypec.IDENTITYVERIFYFAILED,0)
        NetSocketFun.NetSocketSend(session.sockfd,msghead)
        
if __name__ == "__main__":
    import os
