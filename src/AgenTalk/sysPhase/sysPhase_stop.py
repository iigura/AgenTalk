# [ AgenTalk ]

import AgenTalk

def init():
    return AgenTalk.param.SystemPhaseID_Stop

@AgenTalk.fastpass
def act():
    print(f"=== RECV STOP ===")

