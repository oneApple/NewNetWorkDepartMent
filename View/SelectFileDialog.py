# -*- coding: UTF-8 -*-
import wx
   
class SelectFileDialog(wx.SingleChoiceDialog):
    def __init__(self,netconnect,filelist):
        super(SelectFileDialog,self).__init__(None,"选择文件","选择文件",filelist)
        self.netconnect = netconnect
   
    def secondButtonFun(self):
        _choice = self.GetStringSelection()
        self.netconnect.ReqFile(_choice)
        self.Destroy()
        
    def firstButtonFun(self):
        pass
   
    def Run(self):
        _res = self.ShowModal()
        if _res == wx.ID_OK:
            self.secondButtonFun()
        elif _res == wx.ID_CANCEL:
            self.firstButtonFun()
        self.Destroy()
   
if __name__=='__main__':
    app = wx.App()
    f = SelectFileDialog("选择文件")
    f.Run()
    app.MainLoop()