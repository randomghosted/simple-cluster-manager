import docker
import clusterManager as cm

class clusterVolumeManager:
    
    def __init__(self,client=docker.from_env()):
        self.volumeId=0;
        self.volumeNamePrefix="Volume-";
        self.client=client;
        
    def createVolume(self,numberOfVolumes):
        volumes=[];
        for i in range(numberOfVolumes):
            self.volumeId+=1;
            volume=self.client.volumes.create(name=self.volumeNamePrefix+str(self.volumeId));
            volumes.append(volume);
        return volume;
    
    def getAllVolumes(self):
        return self.client.volumes.list();
    
    def getSpecifiedVolume(self,volumeNameOrId):
        return self.client.volumes.get(volumeNameOrId);
    
    def removeVolumes(self,volumeNameOrIdList):
        for i in volumeNameOrIdList:
            self.getSpecifiedVolume(i).remove();
            
    def showVolumes(self):
        volumesList=self.getAllVolumes();
        print("name\tid\t");
        for i in volumesList:
            print(i.name+"\t"+i.id+"\t");
        
    def bindVolumeToaContianer(self,volumeName,containerId):
        None;
    
    def showUsedVolume(self):
        None;
        
    def showVolumeContent(self):
        None;
        