# -*- coding: UTF-8 -*-
import wx, string, os
from wx.lib.pubsub  import Publisher

from GlobalData import CommonData, ConfigData, MagicNum, WindowConfig
from DataBase import MediaTable
import MatrixTable, FullScreenFrame

class MyFrame(wx.Frame):
    def __init__(self,_permission,netconnect,msg):
        self.wcfg = WindowConfig.WindowConfig()
        wx.Frame.__init__(self, None, -1, "内容保护子系统-互信系统",size = self.wcfg.GetFrameSize())
        
        self.peername = msg[0]
        self.peerpermission = msg[1]
        self.username = msg[2]
        self.__type = _permission
        
        self.__vbox_top = wx.BoxSizer(wx.VERTICAL)
        self.__hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.__panel_top = wx.Panel(self)
        
        self.createHeadStaticText(text = "您好:" + self.username + ",欢迎使用内容保护子系统-互信系统!"+ "\n")
        self.createHeadStaticText(align = wx.ALIGN_LEFT,text ="\n" + " 网络运营部门" + "\n",\
                                  fontsize = self.wcfg.GetSystemNameFontSize(),\
                                  fontcolor = self.wcfg.GetSystemNameFontColor(),\
                                  backcolor = self.wcfg.GetSystemNameBackColor())
        self.__vbox_top.Add(wx.StaticLine(self.__panel_top), 0, wx.EXPAND|wx.ALL, 5)
        self.createMenuBar()
        
        self.createLeft()
        self.createShowTextCtrl()
        
        self.__vbox_top.Add(self.__hbox,proportion=2,flag = wx.EXPAND)
        self.__vbox_top.Add(wx.StaticLine(self.__panel_top), 0, wx.EXPAND|wx.ALL, 5)
        self.createHeadStaticText(text = "CopyRight@CUC 2013")
        #self.__vbox_top.Add(wx.StaticLine(self.__panel_top), 0, wx.EXPAND|wx.ALL, 5)
        self.__panel_top.SetSizer(self.__vbox_top)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow) 
        self.registerPublisher()
        
        self.__gridNetCurPos = -1
        self.__gridLocalCurPos = -1
        self.__showTextColor = True
        self.__contentList = []
        
        self.fullframe = FullScreenFrame.FullScreenFrame(self,-1,"信息显示区")    
        
        self.netconnect = netconnect
        self.netconnect.ReqFileList()
    
    def OnCloseWindow(self,evt):
        self.Destroy()
        try:
            self.netconnect.StopNetConnect()
            for content in self.__contentList:
                content.StopNetConnect()
        except:
            pass
        import sys
        sys.exit()
    
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
        showmsg = "处理文件:"+ _recvmsg[0] + "\n"
        showmsg += "当前状态:" + _recvmsg[1]
        self.__infoStatic.SetLabel(showmsg)
    
    def refreshNetFileList(self,recvmsg):
        "更新文件列表"
        _filelist = recvmsg.data
        _m = MatrixTable.MatrixTable(_filelist,["文件名","所有者"],[i for i in range(len(_filelist))])
        self.__netFileTable.ClearGrid()#清空表格
        self.__netFileTable.SetTable(_m)
        self.__netFileTable.Hide()
        self.__netFileTable.Show()
        
    def refreshLocalFileList(self,recvmsg = ""):
        "更新文件列表"
        _filelist = self.getLocalFileList()
        _m = MatrixTable.MatrixTable(_filelist,["文件名","所有者"],[i for i in range(len(_filelist))])
        self.__localFileTable.ClearGrid()#清空表格
        self.__localFileTable.SetTable(_m)
        self.__localFileTable.Hide()
        self.__localFileTable.Show()
    
    def getLocalFileList(self):
        "获取文件列表"
        _filelist = []
        _cfg = ConfigData.ConfigData()
        _mediaPath = _cfg.GetMediaPath()
        if not os.path.exists(_mediaPath):
            os.mkdir(_mediaPath)
        
        _db = MediaTable.MediaTable()
        _db.Connect()
        _res = _db.Search("select * from MediaTable")
        _db.CloseCon()
        
        for index in range(len(_res)):
            _singleFile = [_res[index][0], _res[index][1]]
            _filelist.append(_singleFile)
            
        return _filelist
    
    def evtGridRowLabelLeftClick(self,evt):
        "左键单击行标签"
        _pos = evt.GetRow()
        _grid = evt.GetEventObject()
        if _grid == self.__netFileTable:
            _gridCurPos = self.__gridNetCurPos
            self.__gridNetCurPos = _pos
        else:
            _gridCurPos = self.__gridLocalCurPos
            self.__gridLocalCurPos = _pos
        
        if _pos == -1 or _pos == _gridCurPos:
            return
        
        attr = wx.grid.GridCellAttr()
        attr.SetTextColour(self.wcfg.GetTableChoseFontColor())
        attr.SetBackgroundColour(self.wcfg.GetTableChoseBackColor())
        _grid.SetRowAttr(_pos, attr)
        
        if _gridCurPos != -1:
            attr = wx.grid.GridCellAttr()
            _grid.SetRowAttr(_gridCurPos, attr)

        _grid.Hide()
        _grid.Show()
    
    def createLeftFileTable(self,panel,vbox,label):
        "文件列表"
        _panel = self.createPanel(panel)
        _grid = wx.grid.Grid(_panel)
        table = MatrixTable.MatrixTable(self.getLocalFileList(),["文件名","所有者"],[i for i in range(3)])
        _grid.SetTable(table, True)
        _grid.SetRowLabelSize(self.wcfg.GetTableLabelSize())
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.evtGridRowLabelLeftClick)
        
        self.createBox([_grid,], _panel, vbox, label,partition = 2)
        
        return _grid
    
    def createLeft1Static(self,panel,hbox):
        ""
        _panel = self.createPanel(panel)
        
        stext = wx.StaticText(_panel, -1, "")
        stext.SetFont(self.wcfg.GetStaticTextFont())
        stext.SetForegroundColour(self.wcfg.GetStaticTextFontColor())

        self.createBox([stext,], _panel, hbox, "操作结果区")
        
        return stext
    
    def evtBtnRefreshNetFileClick(self,evt):
        self.netconnect.ReqFileList() 
    
    def evtBtnReqFileClick(self,evt):
        _ownername = self.__netFileTable.GetCellValue(self.__gridNetCurPos,1)
        
        from NetCommunication import NetConnect
        _contentSocket = NetConnect.NetConnect(self)
        _cfg = ConfigData.ConfigData();
        addrlist = _cfg.GetContentServerAddress()
        namelist = addrlist[0].split(",")
        iplist = addrlist[1].split(",")
        portlist = addrlist[2].split(",")
        for index in range(len(namelist)):
            if namelist[index] == _ownername:
                if MagicNum.NetConnectc.NOTCONNECT == _contentSocket.StartNetConnect([iplist[index],portlist[index]],_ownername):
                    wx.MessageBox("无法连接服务器","错误",wx.ICON_ERROR|wx.YES_DEFAULT)
                    return
        
        _filename = self.__netFileTable.GetCellValue(self.__gridNetCurPos,0)
        _contentSocket.ReqFile(_filename,self.username)
        self.__contentList.append(_contentSocket)
        self.refreshStaticText([_filename,"接收分发文件"])
        return
    
    def createLeft3Button(self,panel,vbox):
        _panel = self.createPanel(panel)
        
        _Button1 = wx.Button(_panel,-1,"刷新列表")
        self.Bind(wx.EVT_BUTTON,self.evtBtnRefreshNetFileClick ,_Button1)
        _Button2 = wx.Button(_panel,-1,"获取文件")
        self.Bind(wx.EVT_BUTTON,self.evtBtnReqFileClick ,_Button2)
        #self.Bind(wx.EVT_BUTTON,self.evtBtnDelClick ,_Button3)
        
        self.createBox([_Button1,_Button2], _panel, vbox, "",partition = 0.5,align = wx.ALIGN_RIGHT)
    
    def evtBtnDelClick(self,evt):
        "删除按钮触发事件"
        if self.__gridLocalCurPos == -1:
            return
        
        _filename = self.__localFileTable.GetCellValue(self.__gridLocalCurPos,0)
        _ownername = self.__localFileTable.GetCellValue(self.__gridLocalCurPos,1)
        _cfg = ConfigData.ConfigData()
        _path = _cfg.GetMediaPath() + "/" + _ownername + "/" + _filename
        
        _db = MediaTable.MediaTable()
        _db.Connect()
        _db.deleteMedia(_filename,_ownername)
        _db.CloseCon()
        
        try:
            os.remove(_path)
            if os.listdir(_cfg.GetMediaPath() + "/" + _ownername) == []:
                os.rmdir(_cfg.GetMediaPath() + "/" + _ownername)
        except:
            pass
        
        self.__gridLocalCurPos = -1
        self.refreshStaticText([_filename,"删除"])
        self.refreshLocalFileList()
    
    def evtBtnReqIdentifyClick(self,evt):
        "请求责任认定"
        _filename = self.__localFileTable.GetCellValue(self.__gridLocalCurPos,0)
        _ownername = self.__localFileTable.GetCellValue(self.__gridLocalCurPos,1)
        self.netconnect.ReqIdentify(_ownername,_filename)
        self.refreshStaticText([_filename,"正在责任认定"])
    
    def createLeft5Button(self,panel,vbox):
        _panel = self.createPanel(panel)
        
        _Button1 = wx.Button(_panel,-1,"责任认定")
        self.Bind(wx.EVT_BUTTON,self.evtBtnReqIdentifyClick ,_Button1)
        _Button2 = wx.Button(_panel,-1,"删除")
        self.Bind(wx.EVT_BUTTON,self.evtBtnDelClick ,_Button2)
        
        self.createBox([_Button1,_Button2], _panel, vbox, "",partition = 0.5,align = wx.ALIGN_RIGHT)
    
    def createLeft(self):
        "创建左下方的文本显示框"
        panel = self.createPanel(self.__panel_top)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.__infoStatic = self.createLeft1Static(panel,vbox)
        
        vbox.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.ALL, 20)
        
        self.__netFileTable = self.createLeftFileTable(panel,vbox,"已审核的文件")
        self.createLeft3Button(panel, vbox)
        
        vbox.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.ALL, 20)
        
        self.__localFileTable = self.createLeftFileTable(panel,vbox,"已获取的文件")
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
        "添加新行"
        msg = recvmsg.data[0].decode("utf8")
        msg += "\n"
        
        wx.CallAfter(Publisher().sendMessage,CommonData.ViewPublisherc.FULLFRAME_APPENDTEXT,recvmsg.data)
        
        _isChangeColor = recvmsg.data[1]
        if _isChangeColor:
            if self.__showTextColor:
                self.__showText.SetForegroundColour(self.wcfg.GetShowTextFontColor1())
            else:
                self.__showText.SetForegroundColour(self.wcfg.GetShowTextFontColor2())
            self.__showTextColor = not self.__showTextColor
        self.__showText.AppendText(msg)
    
    def evtShowTextDoubleClick(self,evt):
        self.fullframe.ShowFullScreenFrame()
        self.Hide()
    
    def createShowTextCtrl(self):
        "创建右下方的文本显示框"
        _panel = self.createPanel(self.__panel_top)
        
        self.__showText = wx.TextCtrl(_panel, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)  
        self.__showText.SetFont(self.wcfg.GetShowTextFont())
        self.__showText.SetBackgroundColour(self.wcfg.GetShowTextBackColor())
        self.__showText.Bind(wx.EVT_LEFT_DCLICK, self.evtShowTextDoubleClick)
        
        self.createBox([self.__showText, ], _panel, self.__hbox, "信息显示区", 3)
    
    def registerPublisher(self):
        Publisher().subscribe(self.refreshLocalFileList, CommonData.ViewPublisherc.MAINFRAME_REFRESHLOCALFILETABLE)
        Publisher().subscribe(self.refreshNetFileList, CommonData.ViewPublisherc.MAINFRAME_REFRESHNETFILETABLE)
        Publisher().subscribe(self.refreshStaticText, CommonData.ViewPublisherc.MAINFRAME_REFRESHSTATIC)        
        Publisher().subscribe(self.rewriteShowTextCtrl, CommonData.ViewPublisherc.MAINFRAME_REWRITETEXT)    
        Publisher().subscribe(self.appendShowTextCtrl, CommonData.ViewPublisherc.MAINFRAME_APPENDTEXT)    
    
    def createMenuBar(self):
        self.__menuBar = wx.MenuBar()
        for _label in CommonData.MainFramec.menuMap:
            self.createMenu(self.__menuBar, _label, CommonData.MainFramec.menuMap[_label])
        self.SetMenuBar(self.__menuBar)
    
    def createMenu(self,parentMenu,label,child):
        #self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        if type(child) == dict:
            menu = wx.Menu()
            if parentMenu == self.__menuBar: 
                parentMenu.Append(menu, label)
            else:
                parentMenu.AppendMenu(-1, label, menu)
                parentMenu.AppendSeparator()
            for _label in child:
                self.createMenu(menu, _label, child[_label])
        else:
            menuitem = parentMenu.Append(-1, label)
            self.Bind(wx.EVT_MENU, getattr(self, "menu" + child + "Cmd"), menuitem) 
            parentMenu.AppendSeparator()  
    
    def menuClearDisplayCmd(self,event):
        self.__showText.Clear()
        self.fullframe.clearShowText()
    
#    def OnClose(self,event):
#        self.fullframe.Destroy()
#        self.Destroy()
#        self.netconnect.StopNetConnect()
        
            
    def Run(self):
        self.Center()
        self.Show()
        

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyFrame(1,1,1001)
    frame.Run()
    app.MainLoop()