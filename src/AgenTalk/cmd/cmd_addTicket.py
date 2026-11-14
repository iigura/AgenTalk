import sys
import AgenTalk

def printErrorAndExit():
    print('Error: num of tickets must be an positive integer.',file=sys.stderr)
    sys.exit(-1)

def addTickets(n):
    localTicketChannelURL=AgenTalk.LocalTicketChannelURL
    r=AgenTalk.util.getRedisConnection(localTicketChannelURL)
    for i in range(n):
        r.rpush(AgenTalk.param.LocalTicket,'Ticket to Summer')
    return localTicketChannelURL

def getNumOfTickets(s):
    try:
        n=1 if s is None else int(s)
    except ValueError:
        printErrorAndExit()
    if n<0:
        printErrorAndExit()
    return n

def main(configFilePath):
    n=1
    if len(sys.argv)>2:
        n=getNumOfTickets(sys.argv[2])
    AgenTalk.init(configFilePath)
    localTicketChannelURL=addTickets(n)
    if n==1:
        print(f"add a ticket (local ticket channel='{localTicketChannelURL}').")
    else:
        print(f"add {n} tickets (local ticket channel='{localTicketChannelURL}').")

if __name__=='__main__':
	main('../config.yaml')

