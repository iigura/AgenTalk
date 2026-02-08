# [ AgenTalk ]

from pathlib import Path
import util

def init():
    # thisDir=GetThisFileDir()
    # p=Path(thisDir)
    # errDir=p.parent/'error'
    errDir=FromThisFile('../error')
    if not errDir.exists():
        echo(f"error dir ({str(errDir)}) does not exist.")
        return None
    return 'fitText.error',{'errDir':errDir}

def act(errMsg):
    errDir=initExtra('errDir')
    targetFileAbsPath=getSessionInfoValue('absPathStr')
    newFileName=util.genProcessedFileName(targetFileAbsPath)
    destPath=errDir/newFileName
    srcPath=Path(targetFileAbsPath)
    srcPath.rename(destPath)
    echo(f"{errMsg}\n==> moved: {targetFileAbsPath} -> {str(destPath)}")

