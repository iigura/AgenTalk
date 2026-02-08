import AgenTalk

def main(configFilePath):
    AgenTalk.init(configFilePath)
    localTicketChannelURL=AgenTalk.LocalTicketChannelURL
    r=AgenTalk.util.getRedisConnection(localTicketChannelURL)
    r.delete(AgenTalk.param.LocalTicket)
    print(f"Cleared local Ticket (channel='{localTicketChannelURL}').")

if __name__=='__main__':
	main('../config.yaml')

