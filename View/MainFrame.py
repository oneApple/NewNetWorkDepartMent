# -*- coding: UTF-8 -*-
import wx, string, os
from wx.lib.pubsub  import Publisher

from GlobalData import CommonData, ConfigData, MagicNum
from DataBase import MediaTable
import MatrixTable

class MyFrame(wx.Frame):
    def __init__(self,_permission,netconnect,msg):
        wx.Frame.__init__(self, None, -1, "审核部门",size = (1024,800))
        
        self.peername = msg[0]
        self.peerpermission = msg[1]
        self.username = msg[2]
        print msg
        
        self.__vbox_top = wx.BoxSizer(wx.VERTICAL)
        self.__hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.__panel_top = wx.Panel(self)
        
        self.createHeadStaticText(text = "您好:" + self.username + ",欢迎使用CUCAuditSys!"+ "\n")
        self.createHeadStaticText(align = wx.ALIGN_LEFT,text ="\n" + " 中国传媒大学内容审核系统" + "\n",fontsize = 15,fontcolor = "blue",backcolor = "bisque")
        self.__vbox_top.Add(wx.StaticLine(self.__panel_top), 0, wx.EXPAND|wx.ALL, 5)
        self.createMenuBar()
        
        self.createLeft()
        self.createShowTextCtrl()
        
        self.__vbox_top.Add(self.__hbox,proportion=2,flag = wx.EXPAND)
        self.__vbox_top.Add(wx.StaticLine(self.__panel_top), 0, wx.EXPAND|wx.ALL, 5)
        self.createHeadStaticText(text = "CopyRight@CUC 2013")
        #self.__vbox_top.Add(wx.StaticLine(self.__panel_top), 0, wx.EXPAND|wx.ALL, 5)
        self.__panel_top.SetSizer(self.__vbox_top)
        
        self.registerPublisher()
        
        self.__gridCurPos = -1
        self.__showTextColor = True
        
        self.netconnect = netconnect
        self.netconnect.ReqFileList()
    
    def createPanel(self,outpanel,color = "mistyrose"):
        _panel = wx.Panel(outpanel,-1)
        _panel.SetBackgroundColour(color)
        return _panel
    
    def createBox(self,componentlist,innerpanel,outbox,label,partition = 1,align = wx.EXPAND):
        box = wx.StaticBox(innerpanel,-1,label)
        vbox = wx.StaticBoxSizer(box,wx.HORIZONTAL)
        
        for component in componentlist:
            vbox.Add(component,1,align)
        
        innerpanel.SetSizer(vbox)
        outbox.Add(innerpanel,partition,align)
        return vbox    
    
    def createHeadStaticText(self,align = wx.ALIGN_CENTER,fontsize = 10,text = "",fontcolor = "black",backcolor = "white"):
        "创建位于上方的静态显示框"
        panel = self.createPanel(self.__panel_top,backcolor)
        
        stext = wx.StaticText(panel, -1, text)
        Font= wx.Font(fontsize, wx.MODERN, wx.NORMAL, wx.NORMAL)
        stext.SetFont(Font)
        stext.SetForegroundColour(fontcolor)
        stext.SetBackgroundColour(backcolor)
        
        hbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(stext,0,align)
        panel.SetSizer(hbox)
        self.__vbox_top.Add(panel,0,wx.EXPAND)
    
    def refreshStaticText(self,recvmsg):
        "刷新信息显示区"
        _recvmsg = recvmsg
        if type(recvmsg) != list:
            _recvmsg = recvmsg.data
        showmsg = "当前正在处理文件:"+ _recvmsg[0] + "\n"
        showmsg += "当前正在进行操作:" + _recvmsg[1]
        self.__infoStatic.SetLabel(showmsg)
    
    def refreshFileList(self,recvmsg = ""):
        "更新文件列表"
        _filelist = self.getFileList()
        _m = MatrixTable.MatrixTable(_filelist,["文件名","所有者","状态"],[i for i in range(len(_filelist))])
        self.__grid.ClearGrid()#清空表格
        self.__grid.SetTable(_m)
        self.__grid.Hide()
        self.__grid.Show()
    
    def getFileList(self):
        "获取文件列表"
        _filelist = []
        _cfg = ConfigData.ConfigData()
        _mediaPath = _cfg.GetMediaPath()
        if not os.path.exists(_mediaPath):
            os.mkdir(_mediaPath)
        _userDirList = os.listdir(_mediaPath)  
        
        for owner in _userDirList:
            _filenameList = os.listdir(_mediaPath + "/" + owner)
            for filename in _filenameList:
                _db = MediaTable.MediaTable()
                _db.Connect()
                _res = _db.searchMedia(filename, owner)
                _db.CloseCon()
                status = "未审核"
                if _res == []:
                    break
                if _res[0][5] == MagicNum.MediaTablec.AUDIT:
                    status = "已审核"
                _singleFile = [filename,owner,status]
                _filelist.append(_singleFile)
            
        return _filelist
    
    def evtGridRowLabelLeftClick(self,evt):
        "左键单击行标签"
        _pos = evt.GetRow()
        
        if _pos == -1 or _pos == self.__gridCurPos:
            return
        
        attr = wx.grid.GridCellAttr()
        attr.SetTextColour("white")
        attr.SetBackgroundColour("pink")
        self.__grid.SetRowAttr(_pos, attr)
        
        if self.__gridCurPos != -1:
            attr = wx.grid.GridCellAttr()
            self.__grid.SetRowAttr(self.__gridCurPos, attr)
        
        #_filename = self.__grid.GetCellValue(self.__gridCurPos,0)
        #self.refreshStaticText([_filename,"选择"])
        
        self.__gridCurPos = _pos
        self.__grid.Hide()
        self.__grid.Show()
    
    def createLeftFileTable(self,panel,vbox,label):
        "文件列表"
        _panel = self.createPanel(panel)
        self.__grid = wx.grid.Grid(_panel)
        table = MatrixTable.MatrixTable(self.getFileList(),["文件名","所有者","状态"],[i for i in range(3)])
        self.__grid.SetTable(table, True)
        self.__grid.SetRowLabelSize(15)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.evtGridRowLabelLeftClick)
        
        self.createBox([self.__grid,], _panel, vbox, label,partition = 2)
    
    def createLeft1Static(self,panel,hbox):
        ""
        _panel = self.createPanel(panel)
        
        stext = wx.StaticText(_panel, -1, "")
        Font= wx.Font(15, wx.MODERN, wx.NORMAL, wx.NORMAL)
        stext.SetFont(Font)
        stext.SetForegroundColour("black")
        stext.SetBackgroundColour("white")

        self.createBox([stext,], _panel, hbox, "状态显示区")
        
        return stext
    
    def createLeft3Button(self,panel,vbox):
        _panel = self.createPanel(panel)
        
        _Button1 = wx.Button(_panel,-1,"刷新列表")
        #self.Bind(wx.EVT_BUTTON,self.evtBtnAuditClick ,_Button1)
        _Button2 = wx.Button(_panel,-1,"获取文件")
        #self.Bind(wx.EVT_BUTTON,self.evtBtnSamplingClick ,_Button2)
        #self.Bind(wx.EVT_BUTTON,self.evtBtnDelClick ,_Button3)
        
        self.createBox([_Button1,_Button2], _panel, vbox, "",partition = 0.5,align = wx.ALIGN_RIGHT)
    
    def createLeft5Button(self,panel,vbox):
        _panel = self.createPanel(panel)
        
        _Button1 = wx.Button(_panel,-1,"责任认定")
        #self.Bind(wx.EVT_BUTTON,self.evtBtnAuditClick ,_Button1)
        #self.Bind(wx.EVT_BUTTON,self.evtBtnSamplingClick ,_Button2)
        _Button2 = wx.Button(_panel,-1,"删除")
        #self.Bind(wx.EVT_BUTTON,self.evtBtnDelClick ,_Button3)
        
        self.createBox([_Button1,_Button2], _panel, vbox, "",partition = 0.5,align = wx.ALIGN_RIGHT)
    
    def createLeft(self):
        "创建左下方的文本显示框"
        panel = self.createPanel(self.__panel_top)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.__infoStatic = self.createLeft1Static(panel,vbox)
        
        vbox.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.ALL, 20)
        
        self.createLeftFileTable(panel,vbox,"已审核的文件")
        self.createLeft3Button(panel, vbox)
        
        vbox.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.ALL, 20)
        
        self.createLeftFileTable(panel,vbox,"已获取的文件")
        self.createLeft5Button(panel, vbox)
        
        panel.SetSizer(vbox)
        self.__hbox.Add(panel,1,wx.EXPAND)
        #地一个参数是部件，第二个参数是所占比例，1是100,2是50,第三个是排列方式
    
    def rewriteShowTextCtrl(self,recvmsg):
        msg = recvmsg.data
        _text = self.__showText.GetValue()
        self.__showText.Clear()
        _textlist = _text.split("\n")
        _textlist = _textlist[:-2] + [msg,]
        self.__showText.SetValue("\n".join(_textlist) + "\n")
    
    def appendShowTextCtrl(self,recvmsg):
        msg = recvmsg.data
        msg += "\n"
        self.__showText.AppendText(msg)
    
    def createShowTextCtrl(self):
        "创建右下方的文本显示框"
        _panel = self.createPanel(self.__panel_top)
        
        Font= wx.Font(25, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.__showText = wx.TextCtrl(_panel,style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)  
        self.__showText.SetFont(Font)
        self.__showText.SetBackgroundColour("white")
        
        self.createBox([self.__showText,], _panel, self.__hbox, "信息显示区",3)
    
    def registerPublisher(self):
        Publisher().subscribe(self.selectFile, CommonData.ViewPublisherc.MAINFRAME_SELECTFILE)    
        Publisher().subscribe(self.rewriteShowTextCtrl, CommonData.ViewPublisherc.MAINFRAME_REWRITETEXT)    
        Publisher().subscribe(self.appendShowTextCtrl, CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT)    
    
    def createMenuBar(self):
        self.__menuBar = wx.MenuBar()
        for _label in CommonData.MainFramec.menuMap:
            self.createMenu(self.__menuBar, _label, CommonData.MainFramec.menuMap[_label])
        self.SetMenuBar(self.__menuBar)
    
    def createMenu(self,parentMenu,label,child):
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        if type(child) == dict:
            menu = wx.Menu()
            if parentMenu == self.__menuBar: 
                parentMenu.Append(menu, label)
            else:
                parentMenu.AppendMenu(-1, label, menu)
                parentMenu.AppendSeparator()
            for _label in child:
                self.createMenu(menu, _label, child[_label])
#        elif label not in CommonData.MainFramec.disablemenu[self.__type]:
#            menuitem = parentMenu.Append(-1,label)
#            self.Bind(wx.EVT_MENU, getattr(self,"menu" + child + "Cmd"), menuitem) 
#            parentMenu.AppendSeparator()           
    
    def selectFile(self,msg):
        import SelectFileDialog
        _dlg = SelectFileDialog.SelectFileDialog(self.netconnect,msg.data)
        _dlg.Run()
    
    def menuObtainFileCmd(self,event):
        "获取文件"
        self.netconnect.ReqFileList()
        
    def menuIdentifiedCmd(self,event):
        try:
            import ChoseUserAndFileDialog
            _dlg = ChoseUserAndFileDialog.ChoseUserAndFileDialog(self.netconnect)
            _dlg.Run()
        except:
            wx.MessageBox("没有可以选择的文件","错误",wx.ICON_ERROR|wx.YES_DEFAULT)
    
    def menuClearDisplayCmd(self,event):
        self.__showText.Clear()
    
    def menuDeleteMediaCmd(self,event):
        import DeleteMediaDialog
        _dlg = DeleteMediaDialog.DeleteMediaDialog()
        _dlg.Run()
    
    def OnClose(self,event):
        self.Destroy()
        self.netconnect.StopNetConnect()
            
    def Run(self):
        self.Center()
        self.Show()
        

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyFrame(1,1,1001)
    frame.Run()
    app.MainLoop()