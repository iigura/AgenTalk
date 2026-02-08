PCC=None # PseudoCommunicationChannel

def init():
    global PCC
    PCC=[]

def push(msg):
    global PCC
    PCC.append(msg)

def pop():
    global PCC
    return PCC.pop(0)

