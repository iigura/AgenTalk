# [ AgenTalk ]

import AgenTalk

def init():
    return AgenTalk.param.SystemPhaseID_Error

@AgenTalk.fastpass
def act(tracebackStr,failedPhaseName,note):
    print(f"!!! SYSTEM ERROR !!!")
    if tracebackStr is not None:
        print(tracebackStr)
    print(f"  srcMsg={failedPhaseName}")
    print(f"  note  ={note}")

