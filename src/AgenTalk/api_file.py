import os,inspect
from pathlib import Path

def GetThisFileDir(depth=1):
    """
    Returns the directory of the file in which the calling function is defined.
    Parameters:
        depth (int): How many levels up the stack to look.
        depth=1 means the immediate caller (default).
        depth=2 means the caller of the caller, and so on.
    """
    # frame = inspect.currentframe()
    stack=inspect.stack()
    try:
        if len(stack)>depth:
            frame=stack[depth]
            filepath=frame.filename
        # caller_frame = frame.f_back  # 呼び出し元フレーム
        # filepath = inspect.getfile(caller_frame)
            return os.path.dirname(os.path.abspath(filepath))
        else:
            raise IndexError(f"Call stack is not deep enough (depth={depth}).")
    finally:
        # del frame  # メモリリーク防止
        del stack # for memory leak

def FromThisFile(relPath,depth=1):
    """
    Returns the directory of the file in which the calling function is defined.
    Parameters:
        depth (int): How many levels up the stack to look.
        depth=1 means the immediate caller (default).
        depth=2 means the caller of the caller, and so on.
    """
    # frame = inspect.currentframe()
    stack=inspect.stack()
    try:
        if len(stack)>depth:
            frame=stack[depth]
            filepath=frame.filename
        # caller_frame = frame.f_back  # 呼び出し元フレーム
        # filepath = inspect.getfile(caller_frame)
            thisFileDir=os.path.dirname(os.path.abspath(filepath))
            ret=Path(thisFileDir)/relPath            
            return ret
        else:
            raise IndexError(f"Call stack is not deep enough (depth={depth}).")
    finally:
        # del frame  # メモリリーク防止
        del stack # for memory leak


import random, time
from contextlib import contextmanager
from datetime import datetime

@contextmanager
def MakeUniqueFileObj(prefix='',suffix='.txt',dir='.',mode='x',binary=False):
    targetDir=dir  # 内部で分かりやすい名前に
    if binary and "b" not in mode:
        mode += "b"
    while True:
        now=datetime.now()
        filename=now.strftime(f"{prefix}%Y%m%d_%H%M%S_%f")[:-3]+suffix
        filepath=os.path.join(targetDir,filename)
        try:
            f=open(filepath,mode)
            try:
                yield f
            finally:
                f.close()
            break
        except FileExistsError:
            time.sleep(random.randint(1,999)/1000.0)

