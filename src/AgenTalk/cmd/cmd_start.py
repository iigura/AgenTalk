import AgenTalk

def main(configFilePath):
    AgenTalk.init(configFilePath,verbose=True,startRay=True)
    AgenTalk.importSystemPhases()
    AgenTalk.importPhasesBy(configFilePath,recursive=False,verbose=True)
    AgenTalk.setRunningOnHead()
    AgenTalk.start()

if __name__=='__main__':
    main('../../../config.yaml')

