import ast,sys,re
from collections import defaultdict
from pathlib import Path

import AgenTalk

def main(configFilePath,targetPhaseName,argv):
    d=parseArgs(argv)
    # print(d)
    AgenTalk.init(configFilePath)
    session=AgenTalk.newSession(f"RUN:{targetPhaseName}")
    session.invoke(targetPhaseName, *d['args'],**d['kwargs'])

def parseArgs(argv):
    ret={'args':[],'kwargs':{}}
    iterator=iter(argv)
    for token in iterator:
        if token.startswith("--") and "=" in token:
            key,val=token[2:].split("=",1)
            ret['kwargs'][key]=parseToken(val)
        else:
            ret['args'].append(parseToken(token))
    return ret

# safe eval
def parseToken(token):
    match=re.fullmatch(r'path\((.+)\)',token)
    if match:
        pathToken=match.group(1).strip()
        ret=str(Path(pathToken).resolve())
        # print('ABS PATH=',ret)
        return ret
    try:
        return ast.literal_eval(token)
    except:
        return str(token)

if __name__=='__main__':
    if len(sys.argv)<2:
        print('usage: python cmd_run phaseName param1 param2 ...')
        print('ex   : python cmd_run testPhase 11 hello -key1=val1')
        sys.exit(-1)
    targetPhaseName=sys.argv[1]
    # print(f"targetPhaseName='{targetPhaseName}'.")
    main('../../../config.yaml',targetPhaseName,sys.argv[2:])

