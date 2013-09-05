# -*- coding: UTF-8 -*-
import wx
from GlobalData import ConfigData, CommonData
import LoginDialog
   
class SelectServerDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "服务器选择")
        
        _cfg = ConfigData.ConfigData()
        _contentServer = _cfg.GetContentServerAddress()
        _auditServer = _cfg.GetAuditServerAddress()
        self.__server = [_auditServer,_contentServer]
        self.__curType = CommonData.MainFramec.AUDITSERVER
        self.__curServerlist = self.__server[0]
        
        self.__topSizer = wx.BoxSizer(wx.VERTICAL)
        self.createStatic()
        self.createComboBox()
        self.createList()
        self.createButton()
        self.SetSizer(self.__topSizer)
        self.__topSizer.Fit(self)
   
    def createStatic(self):
        self.__text = wx.StaticText(self, -1, "\n请 选 择 服 务 器")
        self.__text.SetForegroundColour("green")
        self.__text.SetBackgroundColour("white")
        
        self.__topSizer.Add(self.__text, 0, wx.ALIGN_CENTER, 5)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
   
    def createComboBox(self):
        self.combo = wx.ComboBox(self, -1, "审核服务器", choices = ["审核服务器","内容服务器"],  size = (300,30),style = wx.CB_DROPDOWN)
        self.combo.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.selectComboBox, self.combo)
        self.__topSizer.Add(self.combo, 0, wx.ALIGN_CENTER, 5)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
    
    def selectComboBox(self,event):
        _index = self.combo.GetSelection()
        _typeList = [CommonData.MainFramec.AUDITSERVER,CommonData.MainFramec.CONTENTSERVER]
        self.__curServerlist = self.__server[_index]
        self.__curType = _typeList[_index]
        _nameList = self.__curServerlist[0].split(",")
        self.listBox.Set(_nameList)
        self.listBox.SetSelection(0)
    
    def createList(self):
        _nameList = self.__server[0][0].split(",")
        self.listBox = wx.ListBox(self, -1, (20, 20), (80, 120), _nameList, wx.LB_SINGLE)
        self.listBox.SetSelection(0)

        self.__topSizer.Add(self.listBox,0,wx.EXPAND)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
    
    def createButton(self):
        auditBt = wx.Button(self,-1,"选择")
        self.Bind(wx.EVT_BUTTON, self.buttonCmd, auditBt)

        self.__topSizer.Add(auditBt,0,wx.ALIGN_RIGHT)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
        
    def buttonCmd(self,event):
        _index = self.listBox.GetSelection()
        _name = self.__curServerlist[0].split(",")
        _ip = self.__curServerlist[1].split(",")
        _port = self.__curServerlist[2].split(",")
        self.Hide()
        _dlg = LoginDialog.LoginDialog(None,self.__curType,_name[_index],_ip[_index],_port[_index])
        _dlg.Run()
        
    def Run(self):
        _res = self.ShowModal()
   
if __name__=='__main__': 
    app = wx.PySimpleApp()
    s = SelectServerDialog()
    s.Run()
    s.Destroy()
    app.MainLoop()