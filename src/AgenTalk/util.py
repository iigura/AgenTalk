import sys,os,copy,runpy,inspect,traceback,re
import importlib.util
from pathlib import Path

import redis

class Error(Exception):
    pass

def genErrStr(msg):
    func=inspect.currentframe().f_back.f_code.co_name
    return f"ERROR: {func} -- {msg}"

def raiseValueError(msg):
    func=inspect.currentframe().f_back.f_code.co_name
    raise ValueError(f"ERROR: {func} -- {msg}")

def dynamicImportFromFile(baseDir,pythonFile):
    # print(f"IN dynamicImportFromFile baseDir={baseDir} pythonFile={pythonFile}")
    cwdBackup       =os.getcwd()
    sysPathBackup   =sys.path.copy()
    sysModulesBackup=sys.modules.copy()
    try:
        os.chdir(baseDir)
        if baseDir not in sys.path:
            sys.path.insert(0,baseDir)
            # print(f"ADDED sys.path '{baseDir}'")
        moduleName=Path(pythonFile).stem
        module=runpy.run_path(os.path.join(baseDir,pythonFile))
        return module,moduleName
    except Exception as e:
        print(f"ERROR: An exception occurred while executing '{pythonFile}'.")
        traceback.print_exc()  # print stack trace.
        return None,None
    finally:
        os.chdir(cwdBackup)
        sys.path=sysPathBackup
        sys.modules.clear()
        sys.modules.update(sysModulesBackup)

def getCallerFunctionName(n=1):
    stack=inspect.stack()
    if len(stack)>n:
        return stack[n].frame.f_code.co_name
    else:
        return None
        
def getCallerFunctionDefinedFilePath(n=1):
    stack=inspect.stack()
    if len(stack)>n:
        frameInfo=stack[n]
        fileName=Path(os.path.abspath(frameInfo.filename)).stem
        return fileName
    else:
        return None 

def getRedisConnection(redisURL):
    ret=redis.from_url(redisURL,decode_responses=True)
    return ret

# Greedily match first JSON object in the output
def getJsonStr(text):
    jsonStrMatch=re.search(r'\{.*\}',text,re.DOTALL)
    if not jsonStrMatch:
        return None
    jsonStr=jsonStrMatch.group(0)
    return jsonStr

