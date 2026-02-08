import inspect,pickle,base64
import redis

from . import param
from . import util

def emptyArgsAndKwargs():
    ret={}
    ret['args'  ]=()
    ret['kwargs']={}
    return ret

class Message:
    def __init__(self,nextPhaseName):
        # print(f"constructor Message nextPhaseName={nextPhaseName}")
        self.phaseName=nextPhaseName
        self.nextActFuncParam={ 'args':(),'kwargs':{} }
        self.execOnHead=False
        self.exitAfterExec=False

    def setNextActFuncParam(self,*args,**kwargs):
        self.nextActFuncParam['args'  ]=args
        self.nextActFuncParam['kwargs']=kwargs

    def getEncodedStr(self):
        encodedBytes=pickle.dumps(self)
        return base64.b64encode(encodedBytes).decode('utf-8')

    def getNextActFuncParam(self):
        return self.nextActFuncParam['args'],self.nextActFuncParam['kwargs']

def decode(encodedStr):
    dataBytes=base64.b64decode(encodedStr)
    ret=pickle.loads(dataBytes)
    return ret

