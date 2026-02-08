# [ AgenTalk ]

from pathlib import Path
import json

def init():
    promptTemplateFile=FromThisFile('../prompts/firstDraft.txt')
    promptTemplateStr=promptTemplateFile.read_text(encoding="utf-8")
    return 'fitText.firstDraft',{'promptTemplateStr':promptTemplateStr}

def act(paramJsonAbsPathStr):
    setSessionInfoKV('absPathStr',paramJsonAbsPathStr) # fitText.error uses this value.
    p=Path(paramJsonAbsPathStr)
    if p.suffix.lower()!='.json':
        invoke('fitText.error',f"should be JSON file: gate/{p.name}")
        return
    jsonFileName=p.name
    jsonFileStem=p.stem
    try:
        with open(paramJsonAbsPathStr,'r',encoding='utf-8') as f:
            jsonObj=json.load(f)
    except:
        invoke('fitText.error',f"can not load JSON: gate/{p.name}")
        return
    if not isinstance(jsonObj,dict):
        invoke('fitText.error',f"JSON root must be a dict object {{ ... }}: gate/{p.name}")
        return
    errMsg_or_jsonObj=checkJson(jsonObj,jsonFileName)
    if isinstance(errMsg_or_jsonObj,str):
        errMsg=errMsg_or_jsonObj
        invoke('fitText.error',errMsg)
        return
    jsonObj=errMsg_or_jsonObj
    topic,notes=getPrompt(jsonObj,jsonFileName)

    setSessionInfoKV('jsonFileName',jsonFileName)
    setSessionInfoKV('jsonFileStem',jsonFileStem)
    setSessionInfoKV('jsonObj',jsonObj)
    setSessionInfoKV('topic',topic)
    setSessionInfoKV('notes',notes)

    echo(f"=== START GENERATION: {jsonFileName}")
    promptTemplateStr=initExtra('promptTemplateStr')
    n=int(jsonObj['target']['chars'])
    r=jsonObj['target']['tolerance_ratio']
    minChars=int(n*(1-r))
    maxChars=int(n*(1+r))
    keywordsStr=', '.join(jsonObj['keywords']['required'])
    themaBlock=f"# テーマ\n{topic}\n\n" if topic is not None else ''
    notesBlock=f"# 追加指示\n{notes}\n\n" if notes is not None else ''
    prompt=promptTemplateStr.format(
            TARGET_CHARS=n,TOLERANCE_PERCENT=r*100,MIN_CHARS=minChars,MAX_CHARS=maxChars,
            REQUIRED_KEYWORDS=keywordsStr,
            THEMA_BLOCK=themaBlock,NOTES_BLOCK=notesBlock)
    # resultJson=GetJsonFromOllama(prompt,callback=echo)
    # echo(f"--- RESULT: {jsonFileName}")
    try:
        resultJson=GetJsonFromOllama(prompt)
    except:
        invoke('fitText.error',f"can not generate a first draft: gate/{jsonFileName}")
        return
    if 'text' not in resultJson:
        invoke('fitText.error',f"can not generate a text: gate/{jsonFileName}")
        return
    text=resultJson['text']
    if minChars<=len(text)<=maxChars:
        echo(text)
        invoke('fitText.finish',text)
    else:
        invoke('fitText.rewrite',text,minChars,maxChars)
        echo(f"rewrite: {jsonFileName} length={len(text)} minChars={minChars} maxChars={maxChars}")

def getPrompt(jsonObj,jsonFileName):
    if 'prompt' not in jsonObj:
        return None,None
    if not isinstance(jsonObj['prompt'],dict):
        invoke('fitText.error',f"JSON.prompt must be a dict object {{ ... }}: gate/{jsonFileName}")
        return None,None
    topic=jsonObj['prompt']['topic'] if 'topic' in jsonObj['prompt'] else None
    notes=jsonObj['prompt']['notes'] if 'notes' in jsonObj['prompt'] else None
    return topic,notes

def checkJson(jsonObj,jsonFileName):
    if 'schema' not in jsonObj:
        return f"JSON data should have 'schema' key: gate/{jsonFileName}"
    if jsonObj['schema']!='fitText':
        return f"JSON.schema should be 'fitText': gate/{jsonFileName}"
    if 'version' not in jsonObj:
        return f"JSON data should have 'version' key: gate/{jsonFileName}"
    if jsonObj['version']<1.0:
        return f"JSON.version must be 1.0 or higher: gate/{jsonFileName}"
    if 'target' not in jsonObj:
        jsonObj['target']={'chars':600,'tolerance=ratio':0.1}
    if not isinstance(jsonObj['target'],dict):
        return f"JSON.target must be a dict object {{ ... }}: gate/{jsonFileName}"
    if 'chars' not in jsonObj['target']:
        jsonObj['target']['chars']=600
    if 'tolerance_ratio' not in jsonObj['target']:
        jsonObj['target']['tolerance_ratio']=0.1
    if 'keywords' not in jsonObj:
        return f"JSON data should have 'keywords' key: gate/{jsonFileName}"
    if not isinstance(jsonObj['keywords'],dict):
        return f"JSON.keywords must be a dict object {{ ... }}: gate/{jsonFileName}"
    if 'required' not in jsonObj['keywords']:
        return f"JSON.keywords should have 'required' key: gate/{jsonFileName}"
    if not isinstance(jsonObj['keywords']['required'],list):
        return f"JSON.keywords.required must be a list object [ ... ]: gate/{jsonFileName}"
    if len(jsonObj['keywords']['required'])<1:
        return f"JSON.keywords.required must have a element at least: gate/{jsonFileName}"
    return jsonObj

