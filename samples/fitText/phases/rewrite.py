# [ AgenTalk ]

from pathlib import Path

def init():
    rewriteMore=FromThisFile('../prompts/rewriteMore.txt').read_text('utf-8')
    rewriteLess=FromThisFile('../prompts/rewriteLess.txt').read_text('utf-8')
    return 'fitText.rewrite',{'rewriteMore':rewriteMore,'rewriteLess':rewriteLess}

def act(text,minChars,maxChars):
    jsonObj=getSessionInfoValue('jsonObj')
    n=int(jsonObj['target']['chars'])
    r=jsonObj['target']['tolerance_ratio']
    keywordsStr=', '.join(jsonObj['keywords']['required'])

    topic=getSessionInfoValue('topic')
    themaBlock=f"# テーマ\n{topic}\n\n" if topic is not None else ''

    notes=getSessionInfoValue('notes')
    notesBlock=f"# 追加指示\n{notes}\n\n" if notes is not None else ''

    template=initExtra('rewriteMore') if len(text)<minChars else initExtra('rewriteLess')    
    prompt=template.format(
            TEXT_BODY=text,
            TARGET_CHARS=n,TOLERANCE_PERCENT=r*100,MIN_CHARS=minChars,MAX_CHARS=maxChars,
            REQUIRED_KEYWORDS=keywordsStr,
            THEMA_BLOCK=themaBlock,NOTES_BLOCK=notesBlock)
    jsonFileName=getSessionInfoValue('jsonFileName')
    try:
        resultJson=GetJsonFromOllama(prompt)
    except:
        invoke('fitText.error',f"can not generate a new text: gate/{jsonFileName}")
        return

    absPathStr=getSessionInfoValue('absPathStr')
    if 'text' not in resultJson:
        invoke('fitText.error',f"can not generate a new text: gate/{jsonFileName}")
        return
    newText=resultJson['text']
    if minChars<=len(newText)<=maxChars:
        echo(newText)
        echo(f"---(len={len(newText)})")
        invoke('fitText.finish',newText)
    else:
        echo(f"rewrite: {jsonFileName} length={len(newText)} minChars={minChars} maxChars={maxChars}")
        invoke('fitText.rewrite',newText,minChars,maxChars)

