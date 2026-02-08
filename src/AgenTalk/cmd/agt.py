# cmd/agt.py

import sys,os

from . import cmd_start,cmd_stop
from . import cmd_clearTicket,cmd_addTicket,cmd_countTicket
from . import cmd_echo
from . import cmd_reg,cmd_run

def helpFunc():
    print(
"""
agt - the AgenTalk utility program

    Usage: agt COMMAND [opt] [param1 param2 ... ]

The following commands are available:

info  - Show system information.  You can also check the Python version.
        Make sure you are using same Python version as the head node.
        No arguments are needed; just run 'agt info'.

start - Start AgenTalk Reactor.
        No arguments are needed; just run 'agt start'.

stop  - Send a STOP message to the Reactor to shut it down.
        No arguments are needed; just run 'agt stop'.

clearTicket (alias: cl)   - Clear the local Ticket.
                            No arguments are needed.
                            You can run either 'agt clearTicket' or 'agt cl'.

addTicket (alias: at)     - Add one local Ticket.
                            No arguments are needed.
                            You can run either 'agt addTicket' or 'agt at'.

countTicket (alias: ct)   - Count the number of local Tickets.
                            No arguments are needed.
                            You can run either 'agt countTicket' or 'agt ct'.

reg  - Register a Phase to the Reactor.
       Takes one argument: the path to a Python file that defines the Phase.
       The file will be loaded and registered to the running Reactor.

       -r Option
       Recursively applies agt reg to the current directory and all subdirectories.

       Example 1: agt reg path/to/phase_definition.py
       Example 2: agt reg -r .

run  - Execute a registered Phase with arguments.

       Usage:
           agt run phaseName ...

       Description:
           Executes the specified Phase identified by `phaseName`.
           Arguments can be passed as positional values or as key-value pairs:
                --key=value

        Examples:
            agt run myPhase arg1 arg2
                -> Runs act(arg1,arg2) in Phase `myPhase`

            Argument expressions like 'path(...)' can be used to automatically convert a
            relative file path into an absolute path.
            For example:
               agt run summarize 'path(sample.txt)'
               -> This will pass the absolute path to 'sample.txt' as a string argument
                  to the 'act' function.

            Note: Be sure to quote the 'path(...)' expression (e.g., with single quotes)
            to prevent shell expansion on Unix-like systems.

echo - Print a message via the Reactor.
       Sends a single string to the Reactor, which prints it
       to the head node's standard output.

       Example:
           agt echo "hello AgenTalk"

help  - Display this message.
""")

def infoFunc():
    major=sys.version_info.major
    minor=sys.version_info.minor
    micro=sys.version_info.micro
    print(f"agt is running on Python {major}.{minor}.{micro}")

def getConfigFilePath():
    thisFilePath=os.path.abspath(__file__)
    thisFileDir =os.path.dirname(thisFilePath)
    configFilePath=os.path.abspath(os.path.join(thisFileDir,'../../../config.yaml'))
    # print(configFilePath)
    return configFilePath
 
def startFunc():
    print('_____ Starting AgenTalk Reactor... _____')
    print("To stop the Reactor, run 'agt stop' from another terminal or press Ctrl-C.")
    configFilePath=getConfigFilePath()
    cmd_start.main(configFilePath)

def stopFunc():
    configFilePath=getConfigFilePath()
    cmd_stop.main(configFilePath)
    print('Send STOP message to the Reactor.')

def clearTicketFunc():
    configFilePath=getConfigFilePath()
    cmd_clearTicket.main(configFilePath)

def addTicketFunc():
    configFilePath=getConfigFilePath()
    cmd_addTicket.main(configFilePath)

def countTicketFunc():
    configFilePath=getConfigFilePath()
    cmd_countTicket.main(configFilePath)

def regFunc(*args):
    if len(args)<1:
        print("Error: 'reg' requires one argument.")
        return
    if args[0]=='-r':
        recursiveMode=True
        targetPath=args[1]
    else:
        recursiveMode=False
        targetPath=args[0]
    configFilePath=getConfigFilePath()
    cmd_reg.main(configFilePath,targetPath,recursive=recursiveMode,verbose=True)

def runFunc(argv):
    configFilePath=getConfigFilePath()
    phaseName=argv[0]
    params=argv[1:]
    # print(f"phaseName='{phaseName}'.")
    # print(f"params={params}")
    cmd_run.main(configFilePath,phaseName,params)

def echoFunc(*args):
    if not args:
        print("Error: 'echo' requires one or more arguments.")
        return
    textStr=' '.join(args)
    configFilePath=getConfigFilePath()
    cmd_echo.main(configFilePath,textStr)

CmdDict={
    'help' :helpFunc,
    'info' :infoFunc,
    'start':startFunc,
    'stop' :stopFunc,
    'clearTicket':clearTicketFunc,
    'cl'         :clearTicketFunc,
    'addTicket'  :addTicketFunc,
    'at'         :addTicketFunc,
    'countTicket':countTicketFunc,
    'ct'         :countTicketFunc,
    'reg'        :regFunc,
    'run'        :runFunc,
    'echo'       :echoFunc,
}

def printShortHelp():
    print("This is the AgenTalk utility program.")
    print("Run 'agt help' for more information.")

def main():
    if len(sys.argv)<2:
        printShortHelp()
        sys.exit(-1)
    cmdStr =sys.argv[1]
    cmdArgs=sys.argv[2:]
    if cmdStr in CmdDict:
        try:
            if cmdStr=='run':
                CmdDict[cmdStr](cmdArgs)
            else:
                CmdDict[cmdStr](*cmdArgs)
        except TypeError as e:
            print(f"Error: Argument mismatch for command '{cmdStr}'.")
            print(f"Details: {e}")
            print("Run `agt help` for usage information.")
    else:
        print(f"Unknown command: {cmdStr}")
        print("Run `agt help` for a list of available commands.")
        sys.exit(-1)

