import AgenTalk

def main(configFilePath):
    AgenTalk.init(configFilePath)
    localTicketChannelURL=AgenTalk.LocalTicketChannelURL
    r=AgenTalk.util.getRedisConnection(localTicketChannelURL)
    n=r.llen(AgenTalk.param.LocalTicket)
    print(f"Number of Tickets: {n} (channel='{localTicketChannelURL}')")

if __name__=='__main__':
	main('../config.yaml')

