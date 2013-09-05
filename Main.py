from View import SelectServerDialog
import wx, sys

reload(sys)                         
sys.setdefaultencoding('utf-8')  
app = wx.PySimpleApp()
s = SelectServerDialog.SelectServerDialog()
s.Run()
s.Destroy()
app.MainLoop()