#coding=utf-8
_metaclass_ = type
import string, struct
from NetCommunication import NetSocketFun
from MsgHandle import MsgHandleInterface
from GlobalData import CommonData, MagicNum, ConfigData
from DataBase import MediaTable
from CryptoAlgorithms import Rsa, HashBySha1
from VideoSampling import ExecuteFfmpeg, GetVideoSampling

class RecvAgroupSignAndParam(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvAgroupSignAndParam,self).__init__()
        _cfg = ConfigData.ConfigData()
        self.__mediapath = _cfg.GetMediaPath()
    
    def handleDhkeyAndAgroupParam(self,ciphertext,session):
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        _plaintext = _rsa.DecryptByPrikey(ciphertext)
        _plist = NetSocketFun.NetUnPackMsgBody(_plaintext)
        if session.sessionkey == _plist[0]:
            self.__aparam = _plist[1:]
            return True
        else:
            return False
    
    def verifySign(self,sign,session):
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        _hbs = HashBySha1.HashBySha1()
        return _rsa.VerifyByPubkey(_hbs.GetHash(self.__sampling.encode("ascii"),MagicNum.HashBySha1c.HEXADECIMAL), sign, session.peername)
    
    def getFrameNum(self,filename):
        "获取目录下文件数即帧的数目"
        import os
        _cfg = ConfigData.ConfigData()
        _dirname = _cfg.GetYVectorFilePath() + filename[:filename.index(".")]
        _framenum = sum([len(files) for root,dirs,files in os.walk(_dirname)])
        return str(_framenum)
    
    def samplingAgroup(self,session):
        _aparam = [string.atoi(s) for s in self.__aparam[:3]]
        _aparam += [string.atof(s) for s in self.__aparam[3:]]
        _meidaPath = self.__mediapath + "/" + session.peername + "/" + session.filename
        #必须绝对路径才可以
        showmsg = "正在采样 ..."
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
        _efm = ExecuteFfmpeg.ExecuteFfmpeg(_meidaPath)
        _efm.Run()
        _efm.WaitForProcess()
        
        import os
        filesize = float(os.path.getsize(_meidaPath)) / (1024 * 1024)
#        showmsg = "采样完成:\n(1)I帧总数：" + self.getFrameNum(session.filename) + \
#                  "\n(2)文件大小(byte)：" + str(filesize)
#        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg, True)
        
        _filename = session.filename[:session.filename.index(".")]
        _gvs = GetVideoSampling.GetVideoSampling(_filename,*_aparam)
        
        showmsg = "A组采样过程："
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg,True)
        self.__sampling = NetSocketFun.NetPackMsgBody(_gvs.GetSampling())
        
        showmsg = "采样完成:\n(1)I帧总数：" + self.getFrameNum(session.filename) + \
                  "\n(2)文件大小(byte)：" + str(filesize)
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg, True)
        
    def addMediaToTable(self,session,sign,hash):
        "添加到数据库"
        _db = MediaTable.MediaTable()
        _value = [session.filename.decode("utf-8"),session.peername.decode("utf8"),NetSocketFun.NetPackMsgBody(self.__aparam),sign,hash]
        _db.Connect()
        _db.AddNewMedia(_value)
        _db.CloseCon()         
             
    def compareSamplingHash(self,recvhash):
        "分组验证"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,"分组进行比对:",True)
        difList = []
        localhash = NetSocketFun.NetUnPackMsgBody(self.__sampling)
        recvlist = NetSocketFun.NetUnPackMsgBody(recvhash)
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
            showmsg = "结果：采样验证成功，该文件在传输过程中未被篡改"
        else:
            showmsg = "结果：采样验证失败，该文件在传输过程中被篡改,其中"
        for _dif in difList:
            showmsg += "\n第" + str(_dif) + "组存在篡改，篡改帧区间为：" + str(_groupborder[_dif]) + "-" + str(_groupborder[_dif + 1]) +"帧"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg)
    
    def deltempFile(self,session):
        "删除临时文件"
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
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        _msglist = NetSocketFun.NetUnPackMsgBody(recvbuffer)
        if self.handleDhkeyAndAgroupParam(_msglist[0], session) == True:
            showmsg = "解密获取参数及采样结果:\n(1)A组参数：\n(帧总数,分组参数,帧间隔位数,混沌初值,分支参数)\n(" + ",".join(self.__aparam) + ")\n(2)A组采样签名：" + _msglist[1] \
                           + "\n(3)本地A组采样：" + CommonData.MsgHandlec.SHOWPADDING.join(NetSocketFun.NetUnPackMsgBody(_msglist[2]))
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg,True)
            
            self.samplingAgroup(session)
            self.deltempFile(session)
            if self.verifySign(_msglist[1], session) == True:
                self.compareSamplingHash(_msglist[2])
                self.addMediaToTable(session,_msglist[1],_msglist[2])
                msghead = self.packetMsg(MagicNum.MsgTypec.RECVMEDIASUCCESS,0)
                NetSocketFun.NetSocketSend(session.sockfd,msghead)
#                showmsg = "收到采样结果:\n(1)A组参数：" + ",".join(self.__aparam) + "\n(2)A组采样签名：" + _msglist[1] \
#                           + "\n(3)本地A组采样：" + CommonData.MsgHandlec.SHOWPADDING.join(NetSocketFun.NetUnPackMsgBody(self.__sampling))
#                showmsg += "\n文件接收并验证成功"
#                self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg,True)
                showmsg = "文件接收并验证成功"
                self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT,showmsg,True)
                self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_REFRESHLOCALFILETABLE,"")
                _msghead = self.packetMsg(MagicNum.MsgTypec.REQCLOSEMSG, 0)
                NetSocketFun.NetSocketSend(session.sockfd,_msghead)
                session.stop()
                return
            else:
                _diflist = self.compareSamplingHash(_msglist[2:])
                showmsg = "采样验证失败，该文件在传输过程中被篡改\n其中第" + ",".join(_diflist) + "组被篡改"
        else:
            showmsg = "会话密钥验证失败,发送方为恶意用户"
        self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg, True)
        msghead = self.packetMsg(MagicNum.MsgTypec.IDENTITYVERIFYFAILED,0)
        NetSocketFun.NetSocketSend(session.sockfd,msghead)
        
if __name__ == "__main__":
    import os
