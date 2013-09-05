# -*- coding: UTF-8 -*-
import wx ,os
from GlobalData import ConfigData
from DataBase import MediaTable
   
class DeleteMediaDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "删除文件")
        
        _cfg = ConfigData.ConfigData()
        self.mediaPath = _cfg.GetMediaPath()
        
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
        try:
            _db = MediaTable.MediaTable()
            _db.Connect()
            _res = _db.Search("select username from MediaTable")
            _db.CloseCon()
            self.userDirList = [r[0] for r in _res] 
        except:
            self.userDirList = []
        if self.userDirList == []:
            self.userDirList = [""]
        self.combo = wx.ComboBox(self, -1, self.userDirList[0], choices = self.userDirList, size = (300,30),style = wx.CB_DROPDOWN)
        self.combo.SetSelection(0)
        self.Bind(wx.EVT_COMBOBOX, self.selectComboBox, self.combo)
        self.__topSizer.Add(self.combo, 0, wx.ALIGN_CENTER, 5)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
    
    def selectComboBox(self,event):
        _index = self.combo.GetSelection()
        _user = self.userDirList[_index]
        
        _db = MediaTable.MediaTable()
        _db.Connect()
        _res = _db.Search("select medianame from MediaTable where username = ?", _user)
        _db.CloseCon()
        
        self.mediaFileList = [m[0] for m in _res]
        self.listBox.Set(self.mediaFileList)
        self.listBox.SetSelection(0)
    
    def createList(self):
        _index = self.combo.GetSelection()
        _user = self.userDirList[_index]
        try:
            _db = MediaTable.MediaTable()
            _db.Connect()
            _res = _db.Search("select medianame from MediaTable where username = ?", [_user])
            _db.CloseCon()
            self.mediaFileList = [m[0] for m in _res]
        except:
            self.mediaFileList = []
        self.listBox = wx.ListBox(self, -1, (20, 20), (80, 120), self.mediaFileList, wx.LB_SINGLE)
        self.listBox.SetSelection(0)

        self.__topSizer.Add(self.listBox,0,wx.EXPAND)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
    
    def createButton(self):
        auditBt = wx.Button(self,-1,"删除")
        self.Bind(wx.EVT_BUTTON, self.buttonCmd, auditBt)

        self.__topSizer.Add(auditBt,0,wx.ALIGN_RIGHT)
        self.__topSizer.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)
        
    def buttonCmd(self,event):
        _index = self.combo.GetSelection()
        _path = self.mediaPath + "/" + self.userDirList[_index]
        _file = _path + "/" + self.mediaFileList[self.listBox.GetSelection()]
        
        _db = MediaTable.MediaTable()
        _db.Connect()
        _db.deleteMedia(self.mediaFileList[self.listBox.GetSelection()],self.userDirList[_index])
        _db.CloseCon()
        
        try:
            print _file
            os.remove(_file)
            if os.listdir(_path) == []:
                os.rmdir(_path)
        except:
            wx.MessageBox("该文件不存在","错误",wx.ICON_ERROR|wx.YES_DEFAULT)
        
        self.Destroy()
        
    def Run(self):
        _res = self.ShowModal()
   
if __name__=='__main__': 
    app = wx.App()
    s = DeleteMediaDialog()
    s.Run()
    app.MainLoop()
