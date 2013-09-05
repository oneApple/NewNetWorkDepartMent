# -*- coding: UTF-8 -*-
import wx
from wx.lib.pubsub  import Publisher

import ValidaDialog
import RegisterDialog
import MainFrame
from GlobalData import MagicNum, CommonData
from NetCommunication import NetConnect

class LoginDialog(ValidaDialog.ValidaDialog,object):
    def __init__(self,netconnect,type):
        super(LoginDialog,self).__init__("登录",MagicNum.ValidaDialogc.IMAGEBUTTON)
        if not netconnect:
            self.__netconnect = NetConnect.NetConnect(self)
            if self.__netconnect.StartNetConnect() == MagicNum.NetConnectc.NOTCONNECT:
                self.setHeaderText("无法连接到服务器，请重新启动") 
        else :
            self.__netconnect = netconnect
        self.__type = type
        self.registerPublisher()
        
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
        _mainFrame = MainFrame.MyFrame(self.__type,self.__netconnect,msg.data +[_inputlist[0],])
        _mainFrame.Run()
        self.Hide()
    
    def secondButtonFun(self):
        _inputlist = self.getInputText()
        if self.__type == CommonData.MainFramec.AUDITSERVER:
            _inputlist[0] = MagicNum.UserTypec.NOUSER + CommonData.MsgHandlec.PADDING + _inputlist[0]
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