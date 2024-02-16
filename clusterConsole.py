from Containers import clusterManager
import utils.printHelp
import argparse

helpTextPath="utils\help.txt";

parser=argparse.ArgumentParser(description="start the manager");
parser.add_argument(type=str,nargs="?",dest="startCommand",help="commandName");
args=parser.parse_args();
command=args.startCommand;
   
if command=="help":
    utils.printHelp.printHelp(helpTextPath);
elif command=="start":
    cm=clusterManager.ClusterManager();
    print("Now you could start typing command line");
    ContinueFlag=True;
    while ContinueFlag:
        ContinueFlag=cm.commandLine_toPerform();
        # try:
        #     ContinueFlag=cm.commandLine_toPerform();
        # except Exception as e:
        #     print(e)
        if ContinueFlag:
            print("---"+"Continue to type command");
else:
    print("you need to first start the manager,type 'help' to get help");