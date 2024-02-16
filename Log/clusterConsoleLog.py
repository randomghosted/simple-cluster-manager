

class consoleLogWriter:
    def __init__(self):
        self.logPath="../logInfo/consoleLog.txt";
    
    def writeLine(self,logging=str):
        with open(self.logPath,"a") as consoleLogFile:
            consoleLogFile.write(logging);
            consoleLogFile.write("\n");
            
