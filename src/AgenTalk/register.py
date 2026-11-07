import sys,os,glob,re,ast,token
from pathlib import Path
import asttokens

from . import param,util

# PhaseFuncDict={}
ActFunc={}
InitExtra={}

sugarCoating=None
def setSugarCoating(coatingFunc):
    global sugarCoating
    sugarCoating=coatingFunc

# --- Register
def importPhase(base,paths,recursive,verbose):
    # print(f"IN imposePhase base={base} path={paths}")
    if not base.startswith('/'):
        raise util.Error(f"config ERROR : phases.base should be start '/' (phaseBase='{base}').")
    for p in paths:
        if p.startswith('/'):
            raise util.Error(f"config ERROR : phases.paths should not be start '/' (phases.path='{p}').")
        absPath=os.path.abspath(os.path.join(base,p))
        if os.path.isdir(absPath):
            importPhasesByDir(absPath,recursive,verbose)
        elif absPath.endswith('.py'):
            importPhaseByFile(base,p,verbose)
        else:
            raise util.Error(f"config ERROR : phases.paths should be directory or python file (phases.path='{p}').")
    # print(f"OUT imposePhase base={base} path={paths}")

def importPhasesByDir(baseDir,recursive,verbose):
    printFlag=False
    pyFiles=list(glob.glob(os.path.join(baseDir,"*.py")))
    for f in pyFiles:
        if hasMagicComment(f):
            if verbose and printFlag==False:
                print(f"importPhasesByDir - {baseDir}")
                printFlag=True
            importPhaseByFile(baseDir,f,verbose,restrict=False)
    if recursive:
        baseDirPath=Path(baseDir).resolve()
        subDirs=[p.resolve() for p in baseDirPath.iterdir() if p.is_dir()]
        for subDir in subDirs:
            importPhasesByDir(subDir,recursive,verbose)

def doInit(module,pythonFilePathStr):
    if 'init' not in module:
        raise util.Error(f"ERROR: no init func at {pythonFilePathStr}")
    initFunc=module['init']
    sugarCoating(initFunc)
    phaseInfo=initFunc()
    if phaseInfo is None:
        raise util.Error(f"ERROR: init error at '{pythonFilePathStr}' ('init' returns None).")
    if isinstance(phaseInfo,str):
        phaseName=phaseInfo
        initExtra=None
    elif isinstance(phaseInfo,tuple):
        phaseName,initExtra=phaseInfo
    if (phaseName is None) or (not isinstance(phaseName,str)):
        raise util.Error(f"ERROR: init error at '{pythonFilePathStr}' (phaseName is not a string).")
    if (initExtra is not None) and (not isinstance(initExtra,dict)):
        raise util.Error(f"ERROR: init error at '{pythonFilePathStr}' (initExtra is not a dict).")
    return phaseName,initExtra
           
def importPhaseByFile(baseDir,pythonFile,verbose,restrict=True):
    absPath=os.path.abspath(os.path.join(baseDir,pythonFile))
    if not isPhase(absPath):
        if restrict:
            raise util.Error(f"ERROR: '{absPath}' is NOT a Phase.")
        else:
            return
    module,moduleName=util.dynamicImportFromFile(baseDir,pythonFile)
    if module is None:
        raise util.Error('module is None (importPhaseByFile).')

    phaseName,initExtra=doInit(module,str(absPath))
    if initExtra is not None:
        global InitExtra
        InitExtra[phaseName]=initExtra

    global ActFunc
    if phaseName in ActFunc:
        raise util.Error(f"ERROR: '{phaseName}' is already registered.")

    ActFunc[phaseName]=module[param.ActFuncName]
    ActFunc[phaseName].__AgenTalk_PhaseName=phaseName
    actFunc=ActFunc[phaseName]
    sugarCoating(actFunc)
    if verbose:
        print(f"Phase '{phaseName}' is loaded.")

def hasMagicComment(pythonFilePath):
    path=Path(pythonFilePath)
    if not path.is_file() or path.suffix != ".py":
        raise util.Error("SYSTEM ERROR at hasMagicComment().")

    source=path.read_text(encoding="utf-8")
    atok=asttokens.ASTTokens(source,parse=True,filename=str(path))
    foundMagicComment=False
    for tok in atok.tokens:
        # Is it the comment at the beginning of the line?
        if tok.type==token.COMMENT and tok.start[1]==0:
            commentText=tok.string.lstrip("#").strip()
            pattern=r'^\s*\[\s*AgenTalk\s*\]'
            if re.match(pattern,commentText):
                foundMagicComment=True
                break
    return foundMagicComment

def isPhase(pythonFilePath):
    path=Path(pythonFilePath)
    if not path.is_file() or path.suffix != ".py":
        raise util.Error("SYSTEM ERROR at isPhase().")

    source=path.read_text(encoding="utf-8")
    hasInit=False
    hasAct =False

    if not hasMagicComment(pythonFilePath): return None
    tree=ast.parse(source,filename=str(path))
    for node in tree.body: # only top-level function
        if isinstance(node,ast.FunctionDef):
            if   node.name==param.InitFuncName: hasInit=True
            elif node.name==param.ActFuncName:  hasAct =True
        if hasInit and hasAct:
            break
    if hasInit==False or hasAct==False:
        print(f"ERROR: invalid Phase. "
             +f"Phase file should have '{param.InitFuncName}' and '{param.ActFuncName}' function ('{pythonFilePath}').")
        return False
    return True

