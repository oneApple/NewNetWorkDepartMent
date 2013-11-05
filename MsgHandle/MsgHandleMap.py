# -*- coding: UTF-8 -*-
_metaclass_ = type
from GlobalData.MagicNum import MsgTypec
from MsgHandle import RecvLoginSuccess, RecvDhGenerateSuccess,IdentifyVerifyFailed,\
                      RecvLoginFail, RecvRegisterFail, RecvRegisterSuccess,RecvAndSendDh ,\
                      RecvFileList, RecvFileBuffer, RecvAllFile, RecvAgroupSignAndParam,\
                      RecvHashElgamal1, RecvHashElgamal2
                      
class MsgHandleMap:
    def __init__(self):
        "消息类型与处理类之间的关系"
        self.__MsgHandleMap = {MsgTypec.SENDDHPANDPUBKEY:RecvAndSendDh.RecvAndSendDh(),
                               MsgTypec.AUDITRETURNDHGENERATE:RecvDhGenerateSuccess.RecvDhGenerateSuccess(),
                               MsgTypec.LOGINSUCCESS:RecvLoginSuccess.RecvLoginSuccess(),
                               MsgTypec.LOGINFAIL:RecvLoginFail.RecvLoginFailed(),
                               
                               MsgTypec.REGISTERFAIL:RecvRegisterFail.RecvRegisterFailed(),
                               MsgTypec.REGISTERSUCCESSMSG:RecvRegisterSuccess.RecvRegisterSuccess(),
                              
                               MsgTypec.SENDFILELIST:RecvFileList.RecvFileList(),
                               MsgTypec.SENDFILEBUFFER:RecvFileBuffer.RecvFileBuffer(),
                               MsgTypec.SENDFILEOVER:RecvAllFile.RecvAllFile(),
                               MsgTypec.SENDAGROUP:RecvAgroupSignAndParam.RecvAgroupSignAndParam(),
                               
                               MsgTypec.SENDHASHELGAMAL1:RecvHashElgamal1.RecvHashElgamal1(),
                               MsgTypec.SENDHASHELGAMAL2:RecvHashElgamal2.RecvHashElgamal2(),
                                               
                               MsgTypec.IDENTITYVERIFYFAILED:IdentifyVerifyFailed.IdentifyVerifyFailed()
                               }
                
    def getMsgHandle(self,msgtype):
        "通过消息类型返回具体的处理类"
        assert(self.__MsgHandleMap.has_key(msgtype))
        return self.__MsgHandleMap[msgtype]