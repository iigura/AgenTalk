from . import param,pcc,message,util
from . import api_ollama

# RunningOnHead=False

class Session:
    def __init__(self,sessionName,messageSender,ticketChannelURL):
        self.name=sessionName
        self.currentPhaseName=None
        self.messageSender=messageSender
        self.ticketChannelURL=ticketChannelURL
        self.sysInfo={}
        self.info={} # session info

    def invoke(self,nextPhaseName,*args,**kwargs):
        "equivalent to session.send(session.msgTo(nextPhaseName,*args,**kwargs))"
        msg=self.msgTo(nextPhaseName,*args,**kwargs)
        self.send(msg)

    def sendToSystem(self,nextPhaseName,*args,**kwargs):
        msg=self.msgTo(nextPhaseName,*args,**kwargs)
        msg.execOnHead=True
        self.send(msg)

    def terminateWith(self,systemPhaseName,*args,**kwargs):
        msg=self.msgTo(systemPhaseName,*args,**kwargs)
        msg.execOnHead=True
        msg.exitAfterExec=True
        self.send(msg)

    def msgTo(self,nextPhaseName,*args,**kwargs):
        msg=message.Message(nextPhaseName)
        msg.setNextActFuncParam(*args,**kwargs)
        self.setMsgBody(msg)
        return msg

    def setMsgBody(self,msg):
        msg.prevPhaseName=self.currentPhaseName
        # msg.mem=self.mem
        msg.ticketChannelURL=self.ticketChannelURL
        msg.session=self

    def sendMsgToAgenTalk(self,systemPhaseID,srcMsg=None):
        newMsg=self.msgToAgenTalk(systemPhaseID,srcMsg)
        self.send(newMsg)

    def setDebugMode(self):
        self.mem[param.DebugModeInfo_Key]=True

    def send(self,msg):
        self.messageSender(msg)

    def echo(self,*args,**kwargs):
        self.sendToSystem(param.SystemPhaseID_Print, *args,**kwargs)

    def setInfo(self,**kwargs):
        self.info.update(kwargs)

    def setInfoKV(self,key,value):
        self.info[key]=value

