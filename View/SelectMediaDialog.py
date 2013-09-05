# -*- coding: UTF-8 -*-
import wx ,os
from GlobalData import ConfigData
   
class SelectMediaDialog(wx.Dialog):
    def __init__(self,title,buttonlable):
        wx.Dialog.__init__(self, None, -1, title)
        
        _cfg = ConfigData.ConfigData()
        self.mediaPath = _cfg.GetMediaPath()
        self.buttonLable = buttonlable
        
        self.__topSizer = wx.BoxSizer(wx.VERTICAL)
        self.createStatic()
        self.createComboBox()
        self.createList()
        self.createButton()
        self.SetSizer(self.__topSizer)
        self.__topSizer.Fit(self)
    
    def createStatic(self):
        self.__text = wx.StaticText(self, -1, "\n请 选 择 文 件")
        self.__text.SetForegroundColour("green")
        self.__text.SetBackgroundColour("white")
        
        self.__topSizer.Add(self.__text, 0, wx.ALIGN_CENTER, 5)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
   
    def createComboBox(self):
        self.userDirList = os.listdir(self.mediaPath)  
        if self.userDirList == []:
            self.userDirList = [""]
        self.combo = wx.ComboBox(self, -1, self.userDirList[0], choices = self.userDirList, size = (300,30),style = wx.CB_DROPDOWN)
        self.combo.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.selectComboBox, self.combo)
        self.__topSizer.Add(self.combo, 0, wx.ALIGN_CENTER, 5)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
    
    def selectComboBox(self,event):
        _index = self.combo.GetSelection()
        _path = self.mediaPath + "/" + self.userDirList[_index]
        self.mediaFileList = os.listdir(_path) 
        self.listBox.Set(self.mediaFileList)
        self.listBox.SetSelection(0)
    
    def createList(self):
        _path = self.mediaPath + "/" + self.userDirList[0]
        self.mediaFileList = os.listdir(_path) 
        self.listBox = wx.ListBox(self, -1, (20, 20), (80, 120), self.mediaFileList, wx.LB_SINGLE)
        self.listBox.SetSelection(0)

        self.__topSizer.Add(self.listBox,0,wx.EXPAND)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
    
    def createButton(self):
        auditBt = wx.Button(self,-1,self.buttonLable)
        self.Bind(wx.EVT_BUTTON, self.buttonCmd, auditBt)

        self.__topSizer.Add(auditBt,0,wx.ALIGN_RIGHT)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
        
    def buttonCmd(self,event):
        pass
        
    def Run(self):
        _res = self.ShowModal()
   
if __name__=='__main__': 
    app = wx.App()
    s = SelectMediaDialog("指标管理","审核")
    s.Run()
    app.MainLoop()
