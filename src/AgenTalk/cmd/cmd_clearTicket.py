import AgenTalk

def main(configFilePath,verbose=True):
    AgenTalk.init(configFilePath)
    localTicketChannelURL=AgenTalk.LocalTicketChannelURL
    r=AgenTalk.util.getRedisConnection(localTicketChannelURL)
    r.delete(AgenTalk.param.LocalTicket)
    if verbose:
        print(f"Cleared local Ticket (channel='{localTicketChannelURL}').")

if __name__=='__main__':
	main('../config.yaml')

