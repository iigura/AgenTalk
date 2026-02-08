import AgenTalk

def main(configFilePath):
    AgenTalk.init(configFilePath)
    session=AgenTalk.newSession('CMD_STOP')
    session.terminateWith(AgenTalk.param.SystemPhaseID_Stop)

if __name__=='__main__':
    main('../../../config.yaml')

