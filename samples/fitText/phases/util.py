from pathlib  import Path
from datetime import datetime

def genProcessedFileName(targetFilePath,withDotSuffix=None):
    srcPath=Path(targetFilePath)
    timestamp=datetime.now().strftime('%y%m%d_%H%M%S')
    suffix=withDotSuffix if withDotSuffix is not None else srcPath.suffix
    ret=f"{srcPath.stem}_{timestamp}{suffix}"
    return ret

