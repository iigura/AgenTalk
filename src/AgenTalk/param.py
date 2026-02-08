RunningOnHead=False
def setRunningOnHead():
    global RunningOnHead
    RunningOnHead=True

FastpassAttrName='_AgenTalk_fastpass_flag'

InitFuncName='init'
ActFuncName='act'

AgenTalkChannel='agenTalk.key:msg'
StopMessage='agenTalk.systemToken:STOP'

LocalTicket='agenTalk.key:local-ticket'

DebugModeInfo_Key='_debugMode'

SystemPhase_SrcMsg_Key   ='_SrcMsg'

# NOTE: phase name '__AgenTalk.*' is reserved.
SystemPhaseID_Error='__AgenTalk.error'
SystemPhaseID_Stop ='__AgenTalk.stop'
SystemPhaseID_Print='__AgenTalk.print'
SystemPhaseID_Reg  ='__AgenTalk.reg'

ErrorMessageTraceback_Key='_errorMessageTraceback'
ErrorMessageNote_Key     ='_errorMessageNote'

SystemPhase_args_Key  ='_systemPhase_args'
SystemPhase_kwargs_Key='_systemPhase_kwargs'

