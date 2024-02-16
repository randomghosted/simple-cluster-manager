import argparse
import pandas as pd
import datetime

# filePath=""

# names=["Container ID","Name","Image","Status","Last Started","LogInfoPath"]
# clusterState=pd.read_csv(filePath,names=names,index="Container ID")

class clusterReader:
    def __init__(self,clusterState):
        self.clusterState=clusterState;
        
    def updateClusterState(self,newClusterState):
        self.clusterState=newClusterState;
    
    def getColumnName(self):
        return self.clusterState.columns.copy();
    
    def readClusterState(self):
        return self.clusterState.copy();
    
    def readName(self):
        return self.clusterState["Name"].copy();
        
    def readImage(self):
        return self.clusterState["Image"].copy();
    
    def readStatus(self):
        return self.clusterState["Last Started"].copy();
    
    def readLogInfoPath(self):
        return self.clusterState["logInfoPath"].copy();
        
    def getExcelCopySheet(self):
        self.clusterState.to_excel("Cluster State Sheet",sheet_name="Cluster State");
        
    
class clusterWriter:
    def __init__(self,clusterState):
        self.clusterState=clusterState;
        
    def addNewContainer(self,ContainerId,Name,Image,Status):
        LastStarted="havn't started yet";
        LogInfoPath="../Log/LogInfo.txt";
        
        self.clusterState.append({
            "container_id":ContainerId,
            "Name":Name,
            "Image":Image,
            "Status":Status,
            "LastStarted":LastStarted,
            "LogInfoPath":LogInfoPath
            })
        
    def deleteSpecifiedContainer_byId(self,containerId):
        for i in range(len(self.clusterState)):
            if self.clusterState.iloc[i]["Container ID"]==containerId:
                self.clusterState=self.clusterState.drop(i,inplace=True);
                break;
            
    def deleteSpecifiedContainer_byName(self,containerName):
        for i in range(len(self.clusterState)):
            if self.clusterState.iloc[i]["Name"]==containerName:
                self.clusterState=self.clusterState.drop(i,inplace=True);
                break;
            
    def updateContainerStatus(self,containerId,newStatus):
        self.clusterState[self.clusterState["Container ID"]==containerId]["Status"]=newStatus;
        
    def updateContainerLastStarted(self,containerId,newLastStarted):
        self.clusterState[self.clusterState["Container ID"]==containerId]["LastStarted"]=newLastStarted;