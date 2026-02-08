import traceback
# from pathlib import Path
import ray

from . import param,util,session,message,register

# Reactor
def getActFunc(phaseName):
    ret=register.ActFunc.get(phaseName)
    if ret is None:
        raise util.Error(f"ERROR: no such phaseName '{phaseName}'.")
    return ret

def Start(mQue,debug=False):
    print( 'AgenTalk: start Phase reactor.')
    getMessage   =mQue.getMessageReceiver()
    messageSender=mQue.getMessageSender()
    try:
        while True:
            msg=getMessage()
            actFunc=getActFunc(msg.phaseName)
            initExtra=register.InitExtra.get(msg.phaseName,None)
            if msg.execOnHead or debug:
                # print(f"msg.phaseName={msg.phaseName}",msg.exitAfterExec)
                execPhaseMain(actFunc,msg,initExtra,messageSender,debug)
                if msg.exitAfterExec:
                    break
            else:
                execPhase.remote(actFunc,msg,initExtra,messageSender)
    except KeyboardInterrupt:
        print('\nAgenTalk: Received Ctrl-C.')
    except util.Error as e:
        print(e)
    finally:
        print('AgenTalk: now stopped Phase reactor.')

def getUpdatedSession(msg,initExtra):
    session=msg.session
    session.initExtra=initExtra    
    session.currentPhaseName=msg.phaseName
    return session

def getTicket(ticketChannelURL):
    r=util.getRedisConnection(ticketChannelURL)
    item=r.blpop(param.LocalTicket)
    _,ticket=item
    return ticket

def releaseTicket(ticketChannelURL,ticketData):
    r=util.getRedisConnection(ticketChannelURL)
    r.rpush(param.LocalTicket,ticketData)

class Ticket:
    def __init__(self,session):
        self.redisURL=session.ticketChannelURL

    def __enter__(self):
        self.ticketData=getTicket(self.redisURL)
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        releaseTicket(self.redisURL,self.ticketData)

@ray.remote
def execPhase(actFunc,msg,initExtra,messageSender):
    execPhaseMain(actFunc,msg,initExtra,messageSender,debug=False)

def debugMode_execPhase(msg,messageSender):
    actFunc  =getActFunc(msg.phaseName)
    initExtra=PhaseSettingDict.get(msg.phaseName,None)
    execPhaseMain(actFunc,msg,initExtra,messageSender,debug=True)

import contextvars
SessionStore=contextvars.ContextVar("AgenTalk.currentSession")

def setIntoSessionStore(s):
    SessionStore.set(s)

def getFromSessionStore():
    return SessionStore.get()

def execPhaseMain(actFunc,msg,initExtra,messageSender,debug=False):
    session=getUpdatedSession(msg,initExtra)
    setIntoSessionStore(session)
    try:
        args,kwargs=msg.getNextActFuncParam()
        if debug or hasattr(actFunc,param.FastpassAttrName):
            # print(f"FASTPASS phase={phaseName} funcName={funcName} hasAttr={hasattr(func,param.FastpassAttrName)}")
            actFunc(*args,**kwargs)
        else:
            # print(f"TICKET phase={phaseName} funcName={funcName} hasAttr={hasattr(func,param.FastpassAttrName)}")
            with Ticket(session):
                actFunc(*args,**kwargs)
    except Exception as e:
        tb=traceback.format_exc() if not isinstance(e,util.Error) else None
        session.terminateWith(param.SystemPhaseID_Error, tb,msg.phaseName,str(e))

