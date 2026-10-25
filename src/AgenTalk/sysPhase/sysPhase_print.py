# [ AgenTalk ]

import AgenTalk

def init():
    return AgenTalk.param.SystemPhaseID_Print

@AgenTalk.fastpass
def act(*args,**kwargs):
    print(*args,**kwargs)

