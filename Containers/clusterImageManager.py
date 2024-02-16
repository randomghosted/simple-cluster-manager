import docker
import clusterManager as cm

class clusterImage:
    def __init__(self,client=docker.from_env()):
        self.client=client;
        
    def getImages(self):
        return self.client.images.list();
        
    def pullImages(self,repositoryNameList):
        for i in repositoryNameList:
            self.client.images.pull(i);
        
    def showDownloadedImages(self):
        imagesList=self.getImages();
        for i in imagesList:
            print(str(i.short_id)+"\t",(i.tags)[0],"\t");