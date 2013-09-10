from View import LoginDialog
import wx, sys

reload(sys)                         
sys.setdefaultencoding('utf-8')  
app = wx.PySimpleApp()
s = LoginDialog.LoginDialog(None,1001)
s.Run()
s.Destroy()
app.MainLoop()
