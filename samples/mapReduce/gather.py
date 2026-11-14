# [ AgenTalk ]

import uuid
import params
import AgenTalk

def init():
    return params.phase.gather

@AgenTalk.fastpass
def act(comKey,numOfWorker):
    r=getGlobalRedisConnection()
    total=0
    for i in range(numOfWorker):
        t=popGlobalRedis(comKey)
        nodeIP=t['nodeIP']
        num=t['num']
        total+=num
        echo(f"RECV from {nodeIP=} {num=}")
    echo(f"GATHER num total={total}")

