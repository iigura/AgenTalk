# [ AgenTalk ]

import AgenTalk

def init():
    return AgenTalk.param.SystemPhaseID_Print

def act(*args,**kwargs):
    print(*args,**kwargs)

