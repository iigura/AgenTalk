# [ AgenTalk ]

import params

def init():
    return params.phase.Go

def act(count,setStartTick,setDeltaTick):
    import time
    nowTick=time.perf_counter()
    deltaTick=nowTick-setStartTick
    echo(f"GO {deltaTick=} {setDeltaTick=}")
    if count>1:
        invoke(params.phase.Ready, count-1)

