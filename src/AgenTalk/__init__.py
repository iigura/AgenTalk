import os,yaml
import ray,redis
from importlib.metadata import version
from pathlib import Path

from . import param,util,pcc,message,reactor,register
from .session import Session
from . import api_ollama,api_mail,api_file
from .mqRedis import RedisMQ
from .mqDebug import DebugMQ

__version__=version('AgenTalk')

# decorator
def fastpass(func):
    setattr(func,param.FastpassAttrName,True)
    return func

RayHeadNodeAddrStr=None
TalkChannelURL=None
LocalTicketChannelURL=None

DefaultLLM=None
DefaultLLM_Key='defaultLLM'

def init(configYamlPath,verbose=False,startRay=False):
    with open(configYamlPath,'r',encoding='utf-8') as f:
        config=yaml.safe_load(f)

    global RayHeadNodeAddrStr
    RayHeadNodeAddrStr=config['rayHeadNodeAddress']
    if startRay:
        ray.init(address=RayHeadNodeAddrStr)

    global TalkChannelURL
    TalkChannelURL=config['talkChannel']

    global LocalTicketChannelURL
    LocalTicketChannelURL=config['localTicketChannel']

    global DefaultLLM
    DefaultLLM=config['defaultLLM']

def getTalkChannelURL():
    return TalkChannelURL

def isInitForProduction():
    return RayHeadNodeAddrStr is not None

def reg(session,targetAbsPath,recursive=True):
    session.sendToSystem(param.SystemPhaseID_Reg, targetAbsPath,recursive)

MqForDebug=None
def debugInit(configYamlPath,verbose=True):
    with open(configYamlPath,'r',encoding='utf-8') as f:
        config=yaml.safe_load(f)
    importSystemPhases()
    global MqForDebug
    MqForDebug=DebugMQ()

def newDebugSession(sessionName):
    if MqForDebug is None:
        raise util.Error('Error (newDebugSession): not initialized for debug. call debugInit().')
    messageSenderForDebug=MqForDebug.getMessageSender()
    session=newSession(sessionName,messageSenderForDebug)
    return session

def debugStart(session,*args):
    if MqForDebug is None:
        raise util.Error('Error (newDebugSession): not initialized for debug. call debugInit().')
    for msg in args:
        session.send(msg)
    reactor.Start(MqForDebug,debug=True)

def importSystemPhases():
    cwd=os.path.dirname(os.path.abspath(__file__))
    sysPhaseDir=os.path.join(cwd,'sysPhase')
    # print(f"sysPhaseDir={sysPhaseDir}")
    register.importPhasesByDir(sysPhaseDir,recursive=False,verbose=False)

def importPhasesBy(configYamlPath,recursive,verbose=False):
    with open(configYamlPath,'r',encoding='utf-8') as f:
        config=yaml.safe_load(f)
    if 'phase' in config:
        if 'base' in config['phase']:
            phaseBase=config['phase']['base']
        else:
            phaseBase=os.path.abspath(os.path.dirname(configYamlPath))
        phasePaths=config['phase']['paths']
        register.importPhase(phaseBase,phasePaths,recursive,verbose)
    else:
        print(f"no phase in {configYamlPath}")

setRunningOnHead=param.setRunningOnHead

def start():
    print(f"connect to Ray head ({RayHeadNodeAddrStr})",flush=True)
    redisMQ=RedisMQ(TalkChannelURL,clear=True)
    reactor.Start(redisMQ)
    ray.shutdown()

def newSession(sessionName,messageSender=None):
    if messageSender is None:
        redisMQ=RedisMQ(TalkChannelURL)
        messageSender=redisMQ.getMessageSender()
    newSession=Session(sessionName,messageSender,LocalTicketChannelURL)
    newSession.sysInfo[DefaultLLM_Key]=DefaultLLM
    return newSession

import inspect
def sugar(targetFunc):
    g=targetFunc.__globals__
    # core
    g['echo'               ]=echo
    g['invoke'             ]=invoke
    g['initExtra'          ]=initExtra
    g['getSession'         ]=getSession
    g['setSessionInfoKV'   ]=setSessionInfoKV
    g['getSessionInfo'     ]=getSessionInfo
    g['getSessionInfoValue']=getSessionInfoValue
    # File
    g['GetThisFileDir'   ]=GetThisFileDir
    g['MakeUniqueFileObj']=MakeUniqueFileObj
    g['FromThisFile'     ]=FromThisFile
    # Text
    g['GetCoreLines'    ]=GetCoreLines
    g['GetValueFromJson']=GetValueFromJson
    # Mail
    g['FetchOldestUnreadMail']=FetchOldestUnreadMail
    g['GetMailBody'          ]=GetMailBody
    g['GetMailSentDate'      ]=GetMailSentDate
    # LLM
    g['Summarize'        ]=Summarize
    g['TranslateToJa'    ]=TranslateToJa
    g['GetJsonFromOllama']=GetJsonFromOllama
register.setSugarCoating(sugar)

getSession=reactor.getFromSessionStore

def getDefaultLLM():
    session=getSession()
    return session.sysInfo[DefaultLLM_Key]

def echo(*args,**kwargs):
    session=getSession()
    session.echo(*args,**kwargs)

def invoke(nextPhaseName,*args,**kwargs):
    session=getSession()
    session.invoke(nextPhaseName,*args,**kwargs)

def initExtra(keyName=None):
    session=getSession()
    if keyName is None:
        return session.initExtra
    else:
        return session.initExtra[keyName]

def setSessionInfo(**kwargs):
    session=getSession()
    session.setInfo(**kwargs)

def setSessionInfoKV(key,value):
    session=getSession()
    session.setInfoKV(key,value)

def getSessionInfo():
    session=getSession()
    return session.info

def getSessionInfoValue(key):
    session=getSession()
    ret=session.info[key]
    return ret

def getPhaseName():
    session=getSession()
    phaseName=session.currentPhaseName
    return phaseName

def GetValueFromJson(jsonData,jsonKey):
    if (jsonData is None) or (jsonKey not in jsonData):
        return None
    ret=jsonData[jsonKey]
    return ret

def raiseError(s):
    phaseName=getPhaseName()
    raise util.Error(f"ERROR ({phaseName}): {s}")

import sys
def addImportPath(*args):
    # print(f"IN addImportPath baseDir={baseDir}")
    cwd=Path(GetThisFileDir(2))
    # print(f"addImportPath baseDir={cwd}")
    # cwd=Path(baseDir).resolve().parent
    for relativePath in args:
        path=cwd/relativePath
        # print(f"  path={path}")
        sys.path.append(str(path.resolve()))
    # print(sys.path)
 
# ===== APIs
import re
from .session import Session

## ---- LLM
def GetOllama(): return api_ollama.OllamaModule

def GetJsonFromOllama(prompt,model=None,callback=None):
    if model is None:
        model=getDefaultLLM()
    # print(f"MODEL={model}")
    return api_ollama.GetJsonFromOllama(prompt,model,callback)

def Summarize(text:str,hint:str='',model=None,errReport=True)->str:
    try:
        if model is None:
            model=getDefaultLLM()
        ret=api_ollama.Summarize(text,hint,model)
        return ret
    except Exception as e:
        if errReport:
            echo(util.genErrStr("Failed to parse JSON output from model."))
            echo("  Raw output:\n",ret)
            echo("  Exception:",e)
        return None

def TranslateToJa(text:str,hint:str='',model:str=None,errReport=True)->str:
    """
    Translates the given text to Japanese using a local LLM via Ollama.
    Ensures output is structured as JSON to avoid extra commentary.

    Args:
        text (str): The source text to translate.
        hint (str): Optional instruction to influence translation style or tone.
        model (str): The model name registered in Ollama.

    Returns:
        str: The translated Japanese text extracted from the JSON output.
    """
    try:
        if model is None:
            model=getDefaultLLM()
        ret=api_ollama.TranslateToJa(text,hint,model)
        return ret
    except Exception as e:
        if errReport:
            echo(util.genErrStr("Failed to parse JSON output from model."))
            echo("  Raw output:\n",ret)
            echo("  Exception:",e)
        return None

## ---- Text
def GetCoreLines(text,startPattern,endPattern,printWarning=True):
    """
    Extracts lines between two regex patterns (inclusive of neither).
    
    Args:
        text (str): The full text from which to extract.
        start_pattern (str): Regex pattern indicating the start marker line.
        end_pattern (str): Regex pattern indicating the end marker line.

    Returns:
        str: The extracted core text between the markers.
    """
    lines=text.splitlines()
    startIndex=endIndex=None
    for i,line in enumerate(lines):
        if startIndex is None and re.search(startPattern,line):
            startIndex=i+1  # exclude the start marker line
        elif startIndex is not None and re.search(endPattern,line):
            endIndex=i      # exclude the end marker line
            break
    if (startIndex is None) and printWarning:
        echo("WARN: GetCoreLines -- START marker not found. Using beginning of text.")
        startIndex=0
    if (endIndex is None) and printWarning:
        echo("WARN: GetCoreLines -- END marker not found. Using end of text.")
        endIndex=len(lines)
    coreLines=lines[startIndex:endIndex]
    return "\n".join(coreLines)

## ---- Mail
FetchOldestUnreadMail=api_mail.FetchOldestUnreadMail

def GetMailBody(mailContents):
    return mailContents[api_mail.kBody]

def GetMailSentDate(mailContents):
    return mailContents[api_mail.kDate]

## ---- file
GetThisFileDir   =api_file.GetThisFileDir
MakeUniqueFileObj=api_file.MakeUniqueFileObj
FromThisFile     =api_file.FromThisFile

