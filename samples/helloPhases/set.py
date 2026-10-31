# [ AgenTalk ]
import params

def init():
    return params.phase.Set

def act(count,startTick):
    import time
    nowTick=time.perf_counter()
    deltaTick=nowTick-startTick
    echo(f"SET {deltaTick=}")
    invoke(params.phase.Go, count,nowTick,deltaTick)

