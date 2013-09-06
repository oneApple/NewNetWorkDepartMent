# -*- coding: UTF-8 -*-
class MsgHandlec:
    MSGHEADTYPE = 'ii'
    SAMPLINGTYPE = "fffff"
    PADDING = "###"
    ELGAMALPAD = "######"
    SPARATE = "~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~\n"
    FILEBLOCKSIZE = 10240

class ThreadType:
    CONNECTAP = 10001
    CONNECTCP = 10002

class ViewPublisherc:
    LOGIN_TRYAGAIN = "logintryagain"
    LOGIN_SWITCH = "loginswitch"
    
    REGISTER_TRYAGAIN = "registertryagain"
    REGISTER_SWITCH = "registerswitch"
    
    MAINFRAME_REWRITETEXT = "mainframerewritetext"
    MAINFRAME_APPENDTEXT = "mainframeappendtext"
    MAINFRAME_REFRESHSTATIC = "mainframerefstatic"
    MAINFRAME_REFRESHNETFILETABLE = "mainframerefnetfiletable"
    MAINFRAME_REFRESHLOCALFILETABLE = "mainframereflocalfiletable"
    

class MainFramec:
    AUDITSERVER = 1001
    CONTENTSERVER = 2002
    auditmenu = {"获取文件".decode("utf8"):"ObtainFile"}
    usermenu = {"责任认定".decode("utf8"):"Identified"}
    toolmenu = {"清理屏幕".decode("utf8"):"ClearDisplay"}
    mediamenu = {"删除文件".decode("utf8"):"DeleteMedia"}
    menuMap = {"内容服务".decode("utf8"):auditmenu,"审核服务".decode("utf8"):usermenu,\
               "工具":toolmenu,"文件管理":mediamenu}
    disablemenu = {AUDITSERVER:"获取文件",CONTENTSERVER:"责任认定"}
    
    
class Rsac:
    "密钥及明文长度:对应关系为:1024:128,2048:256"
    KEYLEN = 1024
    PLAINTLEN = 128    
    
class HashBySha1c:
    "哈希后的长度"
    BINARYHASH = 20
    HEXHASH = 40

class SamplingFrameArrayc:
    GROUPPARAMELEN = 7