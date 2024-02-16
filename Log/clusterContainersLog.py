

class clusterContainerLogWriter:
    
    def __init__(self,containerId):
        self.logPath="../Log/ContainerLogInfo/"+str(containerId)+"LogInfo.txt";
        
    def writeLine(self,logging):
        with open(self.logPath,"a") as containerLogFile:
            containerLogFile.write(logging);
            containerLogFile.write("\n");        