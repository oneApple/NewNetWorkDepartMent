# -*- coding: UTF-8 -*-
import wx,os
from wx.lib.pubsub  import Publisher

import ValidaDialog
import RegisterDialog
import MainFrame
from GlobalData import MagicNum, CommonData, ConfigData
from NetCommunication import NetConnect, NetSocketFun

class LoginDialog(ValidaDialog.ValidaDialog,object):
    def __init__(self,netconnect,type):
        super(LoginDialog,self).__init__("登录",MagicNum.ValidaDialogc.IMAGEBUTTON)
        self.CheckConfig()
        if not netconnect:
            self.__netconnect = NetConnect.NetConnect(self)
            config = ConfigData.ConfigData()
            _auditAddress = config.GetAuditServerAddress()
            if self.__netconnect.StartNetConnect(_auditAddress) == MagicNum.NetConnectc.NOTCONNECT:
                self.setHeaderText("无法连接到服务器，请重新启动") 
        else :
            self.__netconnect = netconnect
        self.__type = type
        self.registerPublisher()
    
    def CheckConfig(self):
        try:
            cfg = ConfigData.ConfigData()
            pathmap = {cfg.GetDbPath():"数据库配置不正确",
               cfg.GetYVectorFilePath():"特征提取存放路径配置不正确",
               cfg.GetFfmpegPathAndArgs()[0]:"ffmpeg程序配置不正确",
               cfg.GetFfmpegPathAndArgs()[1]:"ffmpeg参数配置不正确",
               cfg.GetKeyPath():"密钥路径配置不正确",
               }
            for path in pathmap:
                if not os.path.exists(path):
                    self.setHeaderText(pathmap[path])
        except Exception,e:
            self.setHeaderText("配置文件不存在或路径错误")
            os.sys.exit()
    
    def registerPublisher(self):
        Publisher().subscribe(self.tryAgain, CommonData.ViewPublisherc.LOGIN_TRYAGAIN)    
        Publisher().subscribe(self.SwitchView, CommonData.ViewPublisherc.LOGIN_SWITCH)     
        
    def getTextLabel(self):
        _labelList = ["用户名", "密码"]
        return _labelList
    
    def getHeaderText(self):
        _text = """\
                    网 络 运 营 部 门\
                """
        return _text
    
    def SwitchView(self,msg):
        _inputlist = self.getInputText()
        _mainFrame = MainFrame.MyFrame(self.__type,self.__netconnect,msg.data +(_inputlist[0],))
        _mainFrame.Run()
        self.Hide()
    
    def secondButtonFun(self):
        _inputlist = self.getInputText()
        if self.__type == CommonData.MainFramec.AUDITSERVER:
            _inputlist[0] = [MagicNum.UserTypec.NOUSER , _inputlist[0]]
        self.__netconnect.ReqConnect(_inputlist[0], _inputlist[1])
            
    def registerButtonFun(self,event):
        self.Destroy()
        _dlg = RegisterDialog.RegisterDialog(self.__netconnect,self.__type)
        _dlg.Run()
        
        
if __name__=='__main__':
    app = wx.PySimpleApp()
    dlg = LoginDialog(None,1001)
    dlg.Run()
    app.MainLoop()