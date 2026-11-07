# [ AgenTalk ]

from datetime import datetime
from pathlib import Path

import AgenTalk

OutDirKey='outDir'

def init():
    outDirAbsPath='/tmp'
    initExtraDict={
        OutDirKey:outDirAbsPath
    }
    return 'stampAllNodes.main',initExtraDict

@AgenTalk.allnodes
def act():
    outDirAbsPath=initExtra(OutDirKey)    
    nowStr=datetime.now().strftime('%Y%m%d_%H%M%S')
    fileName=f"AgenTalk_stamp_{nowStr}.txt"
    outAbsPath=Path(outDirAbsPath)/fileName
    outAbsPath.touch()
    echo(f"generated {outAbsPath=}")

