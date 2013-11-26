# -*- coding: UTF-8 -*-

_metaclass_ = type
from NetCommunication import NetSocketFun
from MsgHandle import MsgHandleInterface
from GlobalData import MagicNum, CommonData, ConfigData
from CryptoAlgorithms import Elgamal, Rsa, HashBySha1
from DataBase import MediaTable

class RecvDhGenerateSuccess(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvDhGenerateSuccess,self).__init__() 
        _cfg = ConfigData.ConfigData()
        self.__mediapath = _cfg.GetMediaPath()
        
    def getAgroupParam(self,session):
        "获取文件A组采样参数和签名"
        _db = MediaTable.MediaTable()
        _db.Connect()
        session.auditfile = session.control.auditfilename.decode("utf-8")
        session.audituser = session.control.auditusername
        _res = _db.searchMedia(session.auditfile,session.audituser)
        _db.CloseCon()
        return NetSocketFun.NetUnPackMsgBody(_res[0][2])
    
    def getFrameNum(self,filename):
        "获取目录下文件数即帧的数目"
        import os
        _cfg = ConfigData.ConfigData()
        _dirname = _cfg.GetYVectorFilePath() + filename[:filename.index(".")]
        _framenum = sum([len(files) for root,dirs,files in os.walk(_dirname)])
        return str(_framenum)
    
    def samplingAgroup(self,session):
        "利用A组参数采样"
        from VideoSampling import ExecuteFfmpeg, GetVideoSampling
        import string
        _aparam = [string.atoi(s) for s in self.__aparam[:3]]
        _aparam += [string.atof(s) for s in self.__aparam[3:]]
        session.auditfile = session.control.auditfilename.decode("utf-8")
        session.audituser = session.control.auditusername
        _meidaPath = self.__mediapath + "/" + session.audituser + "/" + session.auditfile
        #必须绝对路径才可以
        showmsg = "正在采样 ..."
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
        _efm = ExecuteFfmpeg.ExecuteFfmpeg(_meidaPath)
        _efm.Run()
        _efm.WaitForProcess()
        
#        import os
#        filesize = float(os.path.getsize(_meidaPath)) / (1024 * 1024)
#        showmsg = "采样完成:\n(1)I帧总数：" + self.getFrameNum(session.filename) + \
#                  "\n(2)文件大小（MB）：" + str(filesize)
#        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg,True)
        
        _filename = session.auditfile[:session.auditfile.index(".")]
        
        showmsg = "Ａ组采样过程:"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg, True)
        _gvs = GetVideoSampling.GetVideoSampling(_filename,*_aparam)
        self.__sampling = NetSocketFun.NetPackMsgBody(_gvs.GetSampling())       
        
        import os
        filesize = float(os.path.getsize(_meidaPath)) / (1024 * 1024)
        showmsg = "采样完成:\n(1)I帧总数：" + self.getFrameNum(session.auditfile) + \
                  "\n(2)文件大小（MB）：" + str(filesize)
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg,True)
    
    def getAgroupHash(self,session):
        "获取文件A组采样签名"
#        _db = MediaTable.MediaTable()
#        _db.Connect()
#        session.filename = session.control.auditfilename.decode("utf-8")
#        session.contentname = session.control.auditusername
#        _res = _db.searchMedia(session.filename,session.contentname)
#        _db.CloseCon()
#        _hbs = HashBySha1.HashBySha1()
#        return _res[0][4]
        self.__aparam = self.getAgroupParam(session)
        self.samplingAgroup(session)
        return self.__sampling


    def getCipherText(self,session,params):
        "获取加密内容，加密会话密钥和迪非参数"
        _cfg = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfg.GetKeyPath())
        msglist = [session.sessionkey] + params
        plaintext = NetSocketFun.NetPackMsgBody(msglist)
        return _rsa.EncryptByPubkey(plaintext, session.peername)
    
    def getHashElgamalList(self,session):
        hashlist = NetSocketFun.NetUnPackMsgBody(self.getAgroupHash(session))
        elgamallsit = []
        for cphash in hashlist:
            elgamal1 = session.elgamal.EncryptoList(Elgamal.StringToList(cphash))
            elgamallsit.append(Elgamal.GetStructFmt(elgamal1))
            elgamallsit.append("".join(elgamal1))
        
        return elgamallsit
    
    def packMsgBody(self,session):
        "消息体内容：会话密钥，参数，结构形式，第一次加密"
        _params = Elgamal.GetElgamalParamqp()
        import string
        session.elgamal = Elgamal.Elgamal(*[string.atol(str(s)) for s in _params])
        _cipher = self.getCipherText(session,[str(s) for s in _params])
        _plaintext = [session.control.auditfilename.encode("utf-8") ,session.control.auditusername.encode("utf-8")] \
                     + self.getHashElgamalList(session)
        showmsg = "一次加密Ａ组比特串承诺"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg,True)
        return [repr(_cipher)] + _plaintext
    
    def HandleMsg(self,bufsize,session):
        if session.control.ThreadType == CommonData.ThreadType.CONNECTCP:
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,"开始接收文件(" + session.control.filename + ")...")
            msglist = [session.control.filename.encode("utf8")]
            msgbody = NetSocketFun.NetPackMsgBody(msglist)
            msghead = self.packetMsg(MagicNum.MsgTypec.REQFILEBUFFER, len(msgbody))
            NetSocketFun.NetSocketSend(session.sockfd,msghead + msgbody)
        elif session.control.ThreadType == CommonData.ThreadType.CONNECTAP:
            msglist = self.packMsgBody(session)
            _msgbody = NetSocketFun.NetPackMsgBody(msglist)
            msghead = self.packetMsg(MagicNum.MsgTypec.SENDHASHELGAMAL1, len(_msgbody))
            NetSocketFun.NetSocketSend(session.sockfd,msghead + _msgbody)   
