#coding=utf-8
_metaclass_ = type
import string
from NetCommunication import NetSocketFun

from MsgHandle import MsgHandleInterface
from GlobalData import CommonData, MagicNum, ConfigData
from DataBase import MediaTable
from CryptoAlgorithms import Rsa, HashBySha1, Elgamal

class RecvHashElgamal12(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvHashElgamal12,self).__init__()
    
    def handleDhkeyAndAgroupParam(self,msglist,session):
        "获取对方传来的elgamal"
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        if _rsa.DecryptByPrikey(msglist[0]) == session.sessionkey:
            import struct
            self.__index = string.atoi(msglist[1]) + 1
            self.__recvelgamal1 = struct.unpack(msglist[2],msglist[3])
            self.__recvelgamal2 = struct.unpack(msglist[4],msglist[5])
            self.__compelgamal2 = session.elgamal.EncryptoList(self.__recvelgamal1)
            #self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg)
            return True
        else:
            return False  
    
    def getAgroupHash(self,session):
        "获取文件A组采样hash，如果完成则返回空，否则返回改组采样hash"
        _db = MediaTable.MediaTable()
        _db.Connect()
        _res = _db.searchMedia(session.auditfile,session.audituser)
        _db.CloseCon()
        _hbs = HashBySha1.HashBySha1()
        _hashlist = NetSocketFun.NetUnPackMsgBody(_res[0][4])
        if self.__index >= len(_hashlist):
            return ""
        else:
            return _hashlist[self.__index].encode("ascii")
    
    def getCipherText(self,session,params):
        "对参数和会话密钥进行加密"
        _cfg = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfg.GetKeyPath())
        msglist = [session.sessionkey ] + params
        plaintext = NetSocketFun.NetPackMsgBody(msglist)
        return _rsa.EncryptByPubkey(plaintext, session.peername)
    
    def sendHashELgamal(self,session,hash):
        "发送第一次加密结果"
        _params = Elgamal.GetElgamalParamqp()
        session.elgamal = Elgamal.Elgamal(*[string.atol(str(s)) for s in _params])
        elgamal1 = session.elgamal.EncryptoList(Elgamal.StringToList(hash))
        _cipher = self.getCipherText(session,[str(s) for s in _params])
        _plaintext = [str(self.__index),Elgamal.GetStructFmt(elgamal1),"".join(elgamal1)]
        showmsg = "进行第一次加密，第一次加密结果发送给AP\n"
        showmsg += "进行第二次加密，第二次加密结果发送给AP"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg)
        msglist = [_cipher] + _plaintext
        _msgbody = NetSocketFun.NetPackMsgBody(msglist)
        _msghead = self.packetMsg(MagicNum.MsgTypec.SENDHASHELGAMAL1, len(_msgbody))
        NetSocketFun.NetSocketSend(session.sockfd,_msghead + _msgbody)
    
    
    def IdentifyResponsibility(self,session,index):
        "进行责任认定"
        if not Elgamal.CompareStringList(self.__recvelgamal2,self.__compelgamal2):
            #比较接受到的hash和本地保存的hash
            #self.compareSamplingHash(self.__APahash,self.__NoaHash) 
            showmsg = "第" + str(index) + "组出错" 
            session.difList.append(index)
        else:
            #self.compareSamplingHash(self.__APahash,self.__NoaHash)
            showmsg = "第" + str(index) + "组无错误"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
    
    def getAgroupHashAndParam(self,session):
        "获取文件A组采样参数和签名"
        _db = MediaTable.MediaTable()
        _db.Connect()
        session.auditfile = session.control.auditfilename.decode("utf-8")
        session.audituser = session.control.auditusername
        _res = _db.searchMedia(session.auditfile,session.audituser)
        _db.CloseCon()
        self.__aparam = NetSocketFun.NetUnPackMsgBody(_res[0][2])
    
    def showresult(self,session):
        import string
        self.getAgroupHashAndParam(session)
        _fnum = string.atoi(self.__aparam[0])
        _gt = string.atoi(self.__aparam[1])
        
        _groupborder = [x * (_fnum / _gt) for x in range(_gt)] + [_fnum]
        
        if len(session.difList) == 0:
            showmsg = "结果：采样验证成功，该文件未被篡改"
        else:
            showmsg = "结果：采样验证失败，该文件被篡改,其中"
        for _dif in session.difList:
            showmsg += "\n第" + str(_dif) + "组存在篡改，篡改帧区间为：" + str(_groupborder[_dif]) + "-" + str(_groupborder[_dif + 1]) +"帧"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
    
    def sendResultToAp(self,session):
        sendList = [str(session.response)]
        for index in session.difList:
            sendList.append(str(index))
        msgbody = NetSocketFun.NetPackMsgBody(sendList)
        msghead = self.packetMsg(MagicNum.MsgTypec.SENDIDENTIFYRES, len(msgbody))
        NetSocketFun.NetSocketSend(session.sockfd,msghead + msgbody)
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        _msglist = NetSocketFun.NetUnPackMsgBody(recvbuffer)
        if self.handleDhkeyAndAgroupParam(_msglist, session) == True:
            self.IdentifyResponsibility(session,string.atoi(_msglist[1]))
            _ahash = self.getAgroupHash(session)
            if _ahash != "":
                self.sendHashELgamal(session,_ahash)
            else:
                self.showresult(session)
                self.sendResultToAp(session)
            return
        else:
            showmsg = "签名验证失败,发送方为恶意用户"
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
        msghead = self.packetMsg(MagicNum.MsgTypec.IDENTITYVERIFYFAILED,0)
        NetSocketFun.NetSocketSend(session.sockfd,msghead)
        
if __name__ == "__main__":
    import os
