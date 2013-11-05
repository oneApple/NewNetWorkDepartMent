#coding=utf-8
_metaclass_ = type
from NetCommunication import NetSocketFun
from MsgHandle import MsgHandleInterface
from GlobalData import CommonData, MagicNum, ConfigData
from CryptoAlgorithms import Rsa, Elgamal
from DataBase import MediaTable

class RecvHashElgamal2(MsgHandleInterface.MsgHandleInterface,object):
    def __init__(self):
        super(RecvHashElgamal2,self).__init__()
    
    def getAgroupParam(self,session):
        "获取文件A组采样参数和签名"
        _db = MediaTable.MediaTable()
        _db.Connect()
        session.auditfile = session.control.auditfilename.decode("utf-8")
        session.audituser = session.control.auditusername
        _res = _db.searchMedia(session.auditfile,session.audituser)
        _db.CloseCon()
        return NetSocketFun.NetUnPackMsgBody(_res[0][2])
    
    def handleRecvMsg(self,msgList,session):
        "获取对方传来的elgamal"
        _cfd = ConfigData.ConfigData()
        _rsa = Rsa.Rsa(_cfd.GetKeyPath())
        if _rsa.DecryptByPrikey(msgList[0]) == session.sessionkey:
            import struct,string
            aparam = self.getAgroupParam(session)
            _fnum = string.atoi(aparam[0])
            _gt = string.atoi(aparam[1])
            _groupborder = [x * (_fnum / _gt) for x in range(_gt)] + [_fnum]
            showmsg = "分组验证结果："
            for index in range(1,len(msgList),2):
                recv_elgamal2 = struct.unpack(msgList[index],msgList[index + 1])
                local_elgamal2 = struct.unpack(session.elgamal2list[index - 1],session.elgamal2list[index])
                sindex = (index - 1) / 2
                if not Elgamal.CompareStringList(local_elgamal2,recv_elgamal2):
                    #比较接受到的hash和本地保存的hash
                    #self.compareSamplingHash(self.__APahash,self.__NoaHash) 
                    showmsg += "\n第" + str(sindex) + "组存在篡改，篡改帧区间为：" + str(_groupborder[sindex]) + "-" + str(_groupborder[sindex + 1]) +"帧"
                else:
                    #self.compareSamplingHash(self.__APahash,self.__NoaHash)
                    showmsg += "\n第" + str(sindex) + "组不存在篡改"
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg,True)
            return True
        else:
            return False  
    
    def HandleMsg(self,bufsize,session):
        recvbuffer = NetSocketFun.NetSocketRecv(session.sockfd,bufsize)
        _msglist = NetSocketFun.NetUnPackMsgBody(recvbuffer)
        if self.handleRecvMsg(_msglist, session) == True:
            showmsg = "此次验证结束"
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg,True)
            return 
        else:
            showmsg = "签名验证失败,发送方为恶意用户"
            self.sendViewMsg(CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT, showmsg,True)
        msghead = self.packetMsg(MagicNum.MsgTypec.IDENTITYVERIFYFAILED,0)
        NetSocketFun.NetSocketSend(session.sockfd,msghead)
        
if __name__ == "__main__":
    import os
