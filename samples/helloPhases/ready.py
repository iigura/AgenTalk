# [ AgenTalk ]

import params

def init():
    return params.phase.Ready

def act(count=1):
    import time
    echo(f"READY ({count=})")
    startTick=time.perf_counter()
    invoke(params.phase.Set, count,startTick)

