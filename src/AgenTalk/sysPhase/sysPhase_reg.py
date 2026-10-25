# [ AgenTalk ]

from pathlib import Path

import AgenTalk

def init():
    return AgenTalk.param.SystemPhaseID_Reg

@AgenTalk.fastpass
def act(targetPhasePath,recursive):
    try:
        path=Path(targetPhasePath)
        if path.is_file():
            baseDirPath=path.resolve().parent
            fileName=path.name
            AgenTalk.register.importPhaseByFile(baseDirPath,fileName,verbose=True)
        else:
            absPath=str(path.resolve())
            AgenTalk.register.importPhasesByDir(absPath,recursive,verbose=True)
    except ValueError as e:
        print(e,'(systemFunc_Reg)')

