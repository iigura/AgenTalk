import sys
from pathlib import Path

import AgenTalk

def main(configFilePath,targetPhasePath,recursive,verbose=False):
    AgenTalk.init(configFilePath)
    session=AgenTalk.newSession(f"REG:{targetPhasePath}")
    absPath=Path(targetPhasePath).resolve()
    if verbose:
        print(f"registered '{absPath}'.")
    session.sendToSystem(AgenTalk.param.SystemPhaseID_Reg, absPath,recursive)

if __name__=='__main__':
    if (len(sys.argv)<2) or(len(sys.argv)>=3 and sys.argv[1]!='-r'):
        print('usage: python cmd_reg.py [-r] phaseFilePath')
        sys.exit(-1)
    if len(sys.argv)==2:
        recursiveMode=False
        targetPath=sys.argv[1]
    else:
        recursiveMode=True
        targetPath=sys.argv[2]
    main('../../../config.yaml',targetPath,recursive=recursiveMode,verbose=True)
    print('send register Phase message.')

