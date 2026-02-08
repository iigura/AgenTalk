import sys
import AgenTalk

def main(configFilePath,textStr):
    AgenTalk.init(configFilePath)
    session=AgenTalk.newSession('ECHO')
    session.echo(textStr)

if __name__=='__main__':
    if len(sys.argv)<2:
        print('usage: python cmd_echo.py "TEST MESSAGE"')
        sys.exit(-1)
    main('../../../config.yaml',sys.argv[1])

