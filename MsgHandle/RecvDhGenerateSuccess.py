# -*- coding: UTF-8 -*-

_metaclass_ = type

from MsgHandle import MsgHandleInterface
from GlobalData import MagicNum, CommonData, ConfigData
from CryptoAlgorithms import Elgamal, Rsa, HashBySha1
from DataBase import MediaTable

class RecvDhGenerateSuccess(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvDhGenerateSuccess,self).__init__() 
    
    def getAgroupSign(self,session):
        "获取文件A组采样签名"
        _db = MediaTable.MediaTable()
        _db.Connect()
        session.filename = session.control.auditfilename.decode("utf-8")
        session.contentname = session.control.auditusername
        _res = _db.searchMedia(session.filename,session.contentname)
        _db.CloseCon()
        _hbs = HashBySha1.HashBySha1()
        return _hbs.GetHash(_res[0][3],MagicNum.HashBySha1c.HEXADECIMAL)

    def getCipherText(self,session,params):
        "获取加密内容，加密会话密钥和迪非参数"
        _cfg = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfg.GetKeyPath())
        plaintext = session.sessionkey + CommonData.MsgHandlec.PADDING + CommonData.MsgHandlec.PADDING.join(params)
        return _rsa.EncryptByPubkey(plaintext, session.peername)
    
    def packMsgBody(self,session):
        "消息体内容：会话密钥，参数，结构形式，第一次加密"
        _params = Elgamal.GetElgamalParamqp()
        import string
        session.elgamal = Elgamal.Elgamal(*[string.atol(str(s)) for s in _params])
        elgamal1 = session.elgamal.EncryptoList(Elgamal.StringToList(self.getAgroupSign(session)))
        _cipher = self.getCipherText(session,[str(s) for s in _params])
        _plaintext = session.control.auditfilename + CommonData.MsgHandlec.PADDING + \
                     session.control.auditusername + CommonData.MsgHandlec.PADDING + \
                     Elgamal.GetStructFmt(elgamal1) + CommonData.MsgHandlec.PADDING + \
                     "".join(elgamal1)
        showmsg = "A组签名的elgamal加密：\n(1)第一次加密:" + ",".join(elgamal1)
        #self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg)
        return _cipher + CommonData.MsgHandlec.PADDING + _plaintext
    
    def HandleMsg(self,bufsize,session):
        if session.control.ThreadType == CommonData.ThreadType.CONNECTCP:
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,"开始接收文件(" + session.control.filename + ")")
            msgbody = session.control.filename
            msghead = self.packetMsg(MagicNum.MsgTypec.REQFILEBUFFER, len(msgbody))
            session.sockfd.send(msghead + msgbody)
        elif session.control.ThreadType == CommonData.ThreadType.CONNECTAP:
            _msgbody = self.packMsgBody(session)
            msghead = self.packetMsg(MagicNum.MsgTypec.SENDSIGNELGAMAL1, len(_msgbody))
            session.sockfd.send(msghead + _msgbody)
