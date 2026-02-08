from . import mqBase
from .mqBase import BaseMQ
from . import param,util,message
from . import pcc

def getMessageBody():
    encodedStr=pcc.pop()
    msg=message.decode(encodedStr)
    return msg

def messageSenderBody(msg):
    encodedStr=msg.getEncodedStr()
    pcc.push(encodedStr)

# every methods run on head node.
class DebugMQ(BaseMQ):
    def __init__(self,*args):
        pcc.init()
        for msg in args:
            messageSenderBody(msg)
        print('!!! messaging by DebugMQ !!!')

    def getMessageReceiver(self):
        return getMessageBody

    # def getMessage(self):
    #     encodedStr=pcc.pop()
    #     msg=message.decode(encodedStr)
    #     return msg

    def getMessageSender(self):
        return messageSenderBody

    # def push(msg):
    #     encodedStr=msg.getEncodedStr()
    #     pcc.push(encodedStr)

