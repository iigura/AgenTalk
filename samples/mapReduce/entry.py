# [ AgenTalk ]

import uuid
import params
import AgenTalk

def init():
    return params.phase.entry

@AgenTalk.fastpass
def act():
    comKey='_AgenTalk_mapReduce_'+uuid.uuid4().hex    
    echo(f"{comKey=}")
    n=10
    # map (scatter)
    for i in range(1,n+1):
        invoke(params.phase.worker, comKey,i)
    # invoke reduce phase (gather)
    invoke(params.phase.gather, comKey,n)

