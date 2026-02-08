import AgenTalk

def main(configFilePath):
    AgenTalk.init(configFilePath)
    localTicketChannelURL=AgenTalk.LocalTicketChannelURL
    r=AgenTalk.util.getRedisConnection(localTicketChannelURL)
    r.rpush(AgenTalk.param.LocalTicket,'Ticket to Summer')
    print(f"add a ticket (local ticket channel='{localTicketChannelURL}').")

if __name__=='__main__':
	main('../config.yaml')

