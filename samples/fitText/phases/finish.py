# [ AgenTalk ]

from pathlib import Path
import util

def init():
    resultDir =FromThisFile('../result')
    if not resultDir.exists():
        echo(f"error dir ({str(resultDir)}) does not exist.")
        return None
    archiveDir=FromThisFile('../archive')
    if not archiveDir.exists():
        echo(f"error dir ({str(archiveDir)}) does not exist.")
        return None
    return 'fitText.finish',{'resultDir':resultDir,'archiveDir':archiveDir}

def act(text):
    resultDir =initExtra('resultDir')
    srcAbsPathStr=getSessionInfoValue('absPathStr')
    resultFileName=util.genProcessedFileName(srcAbsPathStr,'.txt')
    resultPath=resultDir/resultFileName
    text+=f"\n\n（文字数 {len(text)}）"
    resultPath.write_text(text,encoding='utf-8')

    archiveDir=initExtra('archiveDir')
    archiveFileName=util.genProcessedFileName(srcAbsPathStr)
    destPath=archiveDir/archiveFileName
    srcPath=Path(srcAbsPathStr)
    srcPath.rename(destPath)

    echo(f"FINISH gate/{srcPath.name}")

