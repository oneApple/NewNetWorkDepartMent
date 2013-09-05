#coding=utf-8
_metaclass_ = type
import string

from MsgHandle import MsgHandleInterface
from GlobalData import CommonData, MagicNum, ConfigData
from DataBase import MediaTable
from CryptoAlgorithms import Rsa, HashBySha1, Elgamal
from VideoSampling import ExecuteFfmpeg, GetVideoSampling

class RecvSignElgamal12(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvSignElgamal12,self).__init__()
        _cfg = ConfigData.ConfigData()
        self.__mediapath = _cfg.GetMediaPath()
    
    def getAgroupHashAndParam(self,session):
        "获取文件A组采样参数和签名"
        _db = MediaTable.MediaTable()
        _db.Connect()
        session.auditfile = session.control.auditfilename.decode("utf-8")
        session.audituser = session.control.auditusername
        _res = _db.searchMedia(session.auditfile,session.audituser)
        _db.CloseCon()
        self.__aparam = _res[0][2].split(CommonData.MsgHandlec.PADDING)
        self.__Noasign = _res[0][3]
        self.__NoaHash = _res[0][4]
    
    def handleDhkeyAndAgroupParam(self,msglist,session):
        "获取审核部门的A组签名，并验证该签名是否为审核部门发送"
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        if _rsa.DecryptByPrikey(msglist[0]) == session.sessionkey:
            self.getAgroupHashAndParam(session)
            import struct
            self.__recvelgamal1 = struct.unpack(msglist[1],msglist[2])
            self.__recvelgamal2 = struct.unpack(msglist[3],msglist[4])
            self.__compelgamal2 = session.elgamal.EncryptoList(self.__recvelgamal1)
            #self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg)
            return True
        else:
            return False
    
    def verifySign(self,sign,session):
        "验证采样签名"
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        _hbs = HashBySha1.HashBySha1()
        return _rsa.VerifyByPubkey(_hbs.GetHash(self.__sampling.encode("ascii"),MagicNum.HashBySha1c.HEXADECIMAL), sign, session.contentname)
    
    def getFrameNum(self,filename):
        "获取目录下文件数即帧的数目"
        import os
        _cfg = ConfigData.ConfigData()
        _dirname = _cfg.GetYVectorFilePath() + filename[:filename.index(".")]
        _framenum = sum([len(files) for root,dirs,files in os.walk(_dirname)])
        return str(_framenum)
    
    def samplingAgroup(self,session):
        "利用A组参数采样"
        _aparam = [string.atoi(s) for s in self.__aparam[:3]]
        _aparam += [string.atof(s) for s in self.__aparam[3:]]
        _meidaPath = self.__mediapath + "/" + session.contentname + "/" + session.filename
        #必须绝对路径才可以
        showmsg = "正在采样 ..."
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
        _efm = ExecuteFfmpeg.ExecuteFfmpeg(_meidaPath)
        _efm.Run()
        _efm.WaitForProcess()
        
        import os
        showmsg = CommonData.MsgHandlec.SPARATE +"采样完成:\n(1)总帧数：" + self.getFrameNum(session.filename) + \
                  "\n(2)文件大小(byte)：" + str(os.path.getsize(_meidaPath))
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_REWRITETEXT, showmsg)
        
        _filename = session.filename[:session.filename.index(".")]
        
        showmsg = "Ａ组采样过程:"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, CommonData.MsgHandlec.SPARATE + showmsg)
        _gvs = GetVideoSampling.GetVideoSampling(_filename,*_aparam)
        self.__sampling = CommonData.MsgHandlec.PADDING.join(_gvs.GetSampling())       
    
    def compareSamplingHash(self,localhash,recvhash):
        "分组验证"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, CommonData.MsgHandlec.SPARATE + "分组进行比对:")
        difList = []
        localhash = localhash.split(CommonData.MsgHandlec.PADDING)
        recvlist = recvhash.split(CommonData.MsgHandlec.PADDING)
        for i in range(len(recvlist)):
            try:
                if localhash[i] != recvlist[i]:
                    difList.append(i)
                    showmsg = "第" + str(i) + "组验证失败"
                else:
                    showmsg = "第" + str(i) + "组验证成功"
                self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
            except:
                difList += [index for index in range(i,len(recvlist))]
                break
        
        import string
        _fnum = string.atoi(self.__aparam[0])
        _gt = string.atoi(self.__aparam[1])
        
        _groupborder = [x * (_fnum / _gt) for x in range(_gt)] + [_fnum]
        
        if len(difList) == 0:
            showmsg = "结果：采样验证成功，该文件未被篡改"
        else:
            showmsg = "结果：采样验证失败，该文件被篡改,其中"
        print difList,_groupborder
        for _dif in difList:
            print _dif,_groupborder[_dif],_groupborder[_dif + 1]
            showmsg += "\n第" + str(_dif) + "组存在篡改，篡改帧区间为：" + str(_groupborder[_dif]) + "-" + str(_groupborder[_dif + 1]) +"帧"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
    
    def getCipherText(self,session,params):
        _cfg = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfg.GetKeyPath())
        plaintext = session.sessionkey + CommonData.MsgHandlec.PADDING + CommonData.MsgHandlec.PADDING.join(params)
        return _rsa.EncryptByPubkey(plaintext, session.peername)
    
    def sendHashELgamal(self,session):
        "发送第一次hash加密"
        session.difList = []
        _params = Elgamal.GetElgamalParamqp()
        session.elgamal = Elgamal.Elgamal(*[string.atol(str(s)) for s in _params])
        elgamal1 = session.elgamal.EncryptoList(Elgamal.StringToList(self.__NoaHash.split(CommonData.MsgHandlec.PADDING)[0].encode("ascii")))
        _cipher = self.getCipherText(session,[str(s) for s in _params])
        _plaintext = str(0) + CommonData.MsgHandlec.PADDING + \
                     Elgamal.GetStructFmt(elgamal1) + CommonData.MsgHandlec.PADDING + \
                     "".join(elgamal1)
        #showmsg = "A组采样的elgamal加密:\n(1)组号：" + str(0) + "\n(2)第一次加密结果:" + ",".join(elgamal1)
        #self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg.decode("ascii").encode("ascii"))
        _msgbody = _cipher + CommonData.MsgHandlec.PADDING + _plaintext
        _msghead = self.packetMsg(MagicNum.MsgTypec.SENDHASHELGAMAL1, len(_msgbody))
        session.sockfd.send(_msghead + _msgbody)
    
    def IdentifyResponsibility(self,session):
        "进行责任认定"
        if not Elgamal.CompareStringList(self.__recvelgamal2,self.__compelgamal2):
            #如果二者的签名相同，则比较hash值
            self.sendHashELgamal(session)
            showmsg = "审核部门和运营商保存的内容提供商签名不同，所以内容提供商篡改文件"
        elif not self.verifySign(self.__Noasign, session):
            self.compareSamplingHash(self.__sampling,self.__NoaHash)
            #比较本地采样的hash和本地保存的hash
            showmsg = "文件采样验证失败，所以运营商篡改文件"
        else:
            #self.compareSamplingHash(self.__APahash,self.__NoaHash)
            self.sendHashELgamal(session)
            self.compareSamplingHash(self.__sampling,self.__NoaHash)
            showmsg = "网络运营商和内容提供商无过错"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, CommonData.MsgHandlec.SPARATE + showmsg)
    
    def deltempFile(self,session):
        import os
        _cfg = ConfigData.ConfigData()
        _mediapath = _cfg.GetYVectorFilePath()
        _media = _mediapath + "out.ts" 
        os.remove(_media)
        _dir = _mediapath + session.filename[:session.filename.index(".")]
        for root, dirs, files in os.walk(_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            os.rmdir(root)  
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = session.sockfd.recv(bufsize)
        _msglist = recvbuffer.split(CommonData.MsgHandlec.PADDING)
        if self.handleDhkeyAndAgroupParam(_msglist, session) == True:
            self.samplingAgroup(session)
            self.deltempFile(session)
            self.IdentifyResponsibility(session)
            return
        else:
            showmsg = "签名验证失败,发送方为恶意用户"
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
        msghead = self.packetMsg(MagicNum.MsgTypec.IDENTITYVERIFYFAILED,0)
        session.sockfd.send(msghead)
        
if __name__ == "__main__":
    import os
    print os.getcwd()