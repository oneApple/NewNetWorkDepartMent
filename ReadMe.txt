登录：
发送REQLOGINMSG消息 :发送用户名密码

LOGINSUCCESS:RecvLoginSuccess 登录转入主页面
LOGINFAIL:RecvLoginFail 登录失败


请求分发过程：
REQOBTAINFILE：发送文件名

SENDDHPANDPUBKEY RecvAndSendDh 接受对方发来的迪菲参数p和公钥，首先验证签名是否正确，如果错误关闭线程并发送IDENTITYVERIFYFAILED，
如果正确则生成会话密钥，并发送自己的公钥和签名，SENDDHPUBKEY 

AUDITRETURNDHGENERATE:RecvDhGenerateSuccess: 请求文件REQFILEBUFFER

SENDFILEBUFFER:RecvFileBuffer：接受文件,REQFILEBUFFER

SENDFILEOVER:RecvAllFile：接受文件，并关闭文件 REQAGROUP

SENDAGROUP:RecvAgroupSignAndParam:收到a组参数和a组签名，利用收到的参数在本地采样，然后利用这个参数与a组签名进行验证 RECVMEDIASUCCESS

责任认定过程:
REQIDENTIFIED :发送内容提供商名及文件名 

SENDDHPANDPUBKEY:RecvAndSendDh : 接受对方发来的迪菲参数p和公钥，首先验证签名是否正确，如果错误关闭线程并发送IDENTITYVERIFYFAILED，
如果正确则生成会话密钥，并发送自己的公钥和签名，SENDDHPUBKEY 

AUDITRETURNDHGENERATE:RecvDhGenerateSuccess : 发送第一次加密，消息体内容：会话密钥，参数，结构形式，第一次加密 SENDSIGNELGAMAL1

SENDSIGNELGAMAL12:RecvSignElgamal12 : 进行责任认定，如果
（1）签名不同：
内容商篡改，继续比较hash，确定篡改位置，SENDHASHELGAMAL1
（2）签名相同，文件采样失败，运营商问题
（3）其他是审核问题

SENDHASHELGAMAL12:RecvHashElgamal12 : 验证该组是否被篡改 SENDHASHELGAMAL1




