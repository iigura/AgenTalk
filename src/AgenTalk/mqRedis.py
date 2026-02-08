import types
import redis

from .mqBase import BaseMQ
from . import param,util,message

RedisConnection=None
TalkChannelURL =None

def getMessageBody():
    item=RedisConnection.blpop(param.AgenTalkChannel)
    _,value=item  # (key, value)
    try:
        msg=message.decode(value)
        return msg    
    except Exception as e:
        print(f"[RedisMQ] Invalid decoded string received: {e}")
        return None

class MessageSendByRedis:
    def __init__(self,talkChannelURL,clear=False):
        self.talkChannelURL=talkChannelURL

    def __call__(self,msg):
        # print(f"MessageSendByRedis: phaseName={msg.phaseName}")
        encodedStr=msg.getEncodedStr()
        r=util.getRedisConnection(self.talkChannelURL)
        r.rpush(param.AgenTalkChannel,encodedStr)

class RedisMQ(BaseMQ):
    def __init__(self,talkChannelURL,clear=False):
        self.talkChannelURL=talkChannelURL
        if clear:
            with redis.Redis.from_url(talkChannelURL,decode_responses=True) as r:
                r.delete(param.AgenTalkChannel)
            print('clear all messages.')

    def getMessageReceiver(self):
        if not param.RunningOnHead:
            raise util.Error('SYSTEM ERROR: RedisMQ should be instanciate on HEAD node.')
        global RedisConnection
        if RedisConnection is None:
            RedisConnection=util.getRedisConnection(self.talkChannelURL)
            print(f"talk channel is '{self.talkChannelURL}'.")
        return getMessageBody

    def getMessageSender(self):
        ret=MessageSendByRedis(self.talkChannelURL)
        return ret

