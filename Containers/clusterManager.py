import sys
sys.path.append(".")

import docker
import StateRW.clusterStateRW as RW
import clusterImageManager as cim
import clusterVolumeManager as cvm
import argparse
import sys
import pathlib
import utils.printHelp

class ClusterManager:
    
    def __init__(self):
        self.client=docker.from_env();
        
        #used for construct name
        self.containerNamePrefix="container-";
        self.containerNameId=0;
        
        self.choices=["create","start","stop","list","remove","exec",
                      "images","volumes","parallelproject","pp"];
        
        #used for read or write from cluster state file
        self.writer=RW.clusterWriter("");
        self.reader=RW.clusterReader("");
        
        #used for imageManager and volumeManager
        self.imageManager=cim.clusterImage(self.client);
        self.volumeManager=cvm.clusterVolumeManager(self.client);
        
        self.parser=None;
    
        self.helpTextPath="utils\help.txt";
    
    def createCluster(self,numberOfContainers=int, imageOS=str,volumeConfiguration=dict):
        
        newContainers=[];
        for i in range(numberOfContainers):
            self.containerNameId+=1;
            container=self.client.containers.create(imageOS,
                                          name=(self.containerNamePrefix+str(self.containerNameId)),
                                          hostname=str(self.containerNameId),
                                          volumes=volumeConfiguration,
                                          tty=True,detach=True);
            newContainers.append(container);
        return newContainers;
        
        
    def getRunningContainers(self,print_=True):
        runningContainersList=self.client.containers.list();
        if print_:
            for i,container in enumerate(runningContainersList):
                print(i,container);
        return runningContainersList;
    
    def getAllContainers(self,print_=True):
        allContainersList=self.client.containers.list(all=True);
        if print_:
            for i,container in enumerate(allContainersList):
                print(i,container);
        return allContainersList;
            
    def getStoppedContainers(self,print_=True):
        stoppedContainers=self.client.containers.list(filters={"status":"exited"});
        if print_:
            for i,container in enumerate(stoppedContainers):
                print(i,container);
        return stoppedContainers;
       
    def getPausedContainers(self,print_=True):
        pausedContainers=self.client.containers.list(filters={"status":"paused"});
        if print_:
            for i,container in enumerate(pausedContainers):
                print(i,container);  
        return pausedContainers;   
            
    def getRestartedContainers(self,print_=True):
        restartedContainers=self.client.containers.list(filters={"status":"restarted"});
        if print_:
            for i,container in enumerate(restartedContainers):
                print(i,container);      
        return restartedContainers;
    
    def startCluster(self):
        allContainers=self.getAllContainers(False);
        for i in allContainers:
            i.start();
            
    def stopAllContainers(self,timeout=0):
        allContainers=self.getAllContainers(False);
        for i in allContainers:
            i.stop(timeout=timeout);        
            
    def getSpecifiedContainer(self,containerNameOrId):
        return self.client.containers.get(containerNameOrId);
            
    def getSpecifiedArg(self,currentCommandLine,index):
        parser=argparse.ArgumentParser(description="only to get the operation");
        parser.add_argument(dest="parameters",type=str,nargs="*");
        return parser.parse_args(currentCommandLine.split()).parameters[index]
    
    def cmdExec(self,cmd):
        containers=self.getRunningContainers(False);
        results=[];
        for container in containers:
            result=[];
            exitCode,localResult=container.exec_run(cmd=cmd);
            result.append(container.short_id);
            result.append(container.name);
            result.append(exitCode);
            result.append(localResult);
            results.append(result);
        return results;
    
    def parserRefresher(self):
        self.parser=argparse.ArgumentParser(description="parse the command line of controling the cluster");
        self.parser.add_argument("operation",type=str,nargs="?",help="specify the operation to be performed",choices=self.choices);
    
    def copyFileToaContainer(self,filePath,containerNameOrId,containerInsideTargetPath,newFileName):
        import tarfile as tar
        with tar.open("inter.tar","w") as t:
            t.add(filePath,arcname=newFileName);
        
        with open("inter.tar","rb") as f:
            data=f.read();
            container=self.getSpecifiedContainer(containerNameOrId=containerNameOrId);
            container.put_archive(containerInsideTargetPath,data);
            
        import os
        os.remove("inter.tar");
        
    def listAttrs(self,containers):
        print("short id"+"\t\t"+"name"+"\t\t"+"image"+"\t\t"+"status"+"\t\t")
        for container in containers:
            print(str(container.short_id)+"\t\t"+str(container.name)+"\t\t"+str(container.image)+"\t\t"+str(container.status)+"\t\t")
    
    def removeFileFromaContainer(self,containerNameOrId,containerInsideTargetPath):
        targetContainer=self.getSpecifiedContainer(containerNameOrId=containerNameOrId);
        targetContainer.exec_run(cmd="rm {}"%str(containerInsideTargetPath));
    
    def ParallelProject(self,dataPath,usedPythonScriptPath,usedContainersAmount=int):
        
        self.volumeManager.createVolume(numberOfVolumes=1);
        newVolume=self.volumeManager.getAllVolumes()[-1];
        
        volumeConfiguration={newVolume.name:{"bind":"/home","mode":"rw"}};
        newContainers=self.createCluster(usedContainersAmount,imageOS="python",volumeConfiguration=volumeConfiguration);
        
        data="#!/usr/local/bin/python";
        with open(usedPythonScriptPath,"r") as file:
            data+="\n";
            data+=file.read();
            
        scriptFileNewName="s.py";
        with open(scriptFileNewName,"w") as file:
            file.write(data);
        
        self.copyFileToaContainer(filePath=scriptFileNewName,containerNameOrId=newContainers[0].id,
                                  containerInsideTargetPath="./home",newFileName=scriptFileNewName);
        
        import numpy as np
        import math
        dataMat=np.load(dataPath);
        length=len(dataMat);
        interNpyList=[];
        eachDataLength=math.ceil(length/usedContainersAmount);
        for i in range(usedContainersAmount):
            newContainers[i].start();
            
            interNpyFilePath="data"+str(i+1)+".npy";
            interNpyList.append(interNpyFilePath);
            if (i+1)*eachDataLength>length:
                np.save(interNpyFilePath,dataMat[i*eachDataLength:]);
            else:
                np.save(interNpyFilePath,dataMat[i*eachDataLength:(i+1)*eachDataLength])
               
            newContainers[i].exec_run(cmd="mkdir inter")
            self.copyFileToaContainer(filePath=interNpyFilePath,containerNameOrId=newContainers[i].id,
                                      containerInsideTargetPath="/inter",newFileName="data.npy");
        
        import os
        for i in interNpyList:
            os.remove(i);
            
        resultList=[];
        for i in range(usedContainersAmount):
            newContainers[i].start();
            #newContainers[i].exec_run(cmd="cd /home");
            newContainers[i].exec_run(cmd=str("chmod +x ./home/"+scriptFileNewName));
            exitCode,result=newContainers[i].exec_run(cmd=str("./home/"+scriptFileNewName));
            resultList.append(result);


            newContainers[i].remove(force=True);
        
        newVolume.remove();
        
        os.remove(scriptFileNewName);
        return resultList;
            
        
    def commandLine_toPerform(self):
        self.parserRefresher();
        commandLine=input().strip();
        op=self.getSpecifiedArg(commandLine,0);
        
        #if create
        if op==self.choices[0]:
            self.parser.add_argument("image",type=str,nargs="?",help="the image chosen to apply to the containers");
            self.parser.add_argument("numberOfContainers",type=int,nargs="?",help="number of containers to be created");
            self.parser.add_argument("-v","--volume",dest="volume",type=str,nargs="?",help="volume configuration",action="append");
            
            args=self.parser.parse_args(commandLine.split());
            
            interStrList=args.volume;
            if interStrList==None:
                interStrList=[];
            volumeConfiguration={};
            
            for interStr in interStrList:
                volumeName=interStr.split(":")[0];
                mountPoint=interStr.split(":")[1].split(",")[0];
                authority=interStr.split(",")[1];
                volumeConfiguration[volumeName]={"bind":mountPoint,"mode":authority};
            
            self.createCluster(imageOS=args.image,numberOfContainers=args.numberOfContainers,
                               volumeConfiguration=volumeConfiguration);
            
            return True;
            
        #if start all the containers
        elif op==self.choices[1]:
            self.startCluster();
            
            return True;
        
        #if stop all the containers
        elif op==self.choices[2]:
            self.stopAllContainers();
            
            return True;
        
        #if read the containers with filters
        elif op==self.choices[3]:
            self.parser.add_argument("choice",help="choose containers of which stutas to display",type=str,nargs="?",
                                     choices=["running","exited","all","paused","restarted"]);
            args=self.parser.parse_args(commandLine.split()).choice;
            if args=="all":
                self.listAttrs(self.getAllContainers(False));
            elif args=="running":
                self.listAttrs(self.getRunningContainers(False));
            elif args=="exited":
                self.listAttrs(self.getStoppedContainers(False));
            elif args=="paused":
                self.listAttrs(self.getPausedContainers(False));
            elif args=="restarted":
                self.listAttrs(self.getRestartedContainers(False));
                
            return True;
                
        #if remove a container
        elif op==self.choices[4]:
            self.parser.add_argument("containerNameOrId_list",type=str,nargs="*",help="container name or id used to specify the containers to be deleted");
            args=self.parser.parse_args(commandLine.split()).containerNameOrId_list;
            for i in args:
                container=self.client.containers.get(i);
                container.remove(force=True);
                
            return True;
        
        #if exec the command line
        elif op==self.choices[5]:
            self.parser.add_argument("commandLine",type=str,nargs="*",help="the command line to be executed by each container");
            args=self.parser.parse_args(commandLine.split()).commandLine;
            commandLine="";
            for i in args:
                commandLine+=str(i);
                commandLine+=" ";
            results=self.cmdExec(cmd=commandLine);
            
            print("short_id\tname\texitCode\toutput\t");
            for eachResult in results:
                line="";
                for i in eachResult:
                    line+=(str(i)+"\t");
                print(line);

            return True;
        
        #if used images command line
        elif op==self.choices[6]:
            self.parser.add_argument("concrete operation",type=str,nargs="?",help="the concrete operation to be executed by imagesManager");
            more_1_op=self.getSpecifiedArg(commandLine,1);
            if str(more_1_op)=="list":
                self.imageManager.showDownloadedImages();
            elif str(more_1_op)=="pull":
                self.parser.add_argument("imagesName",type=str,nargs="*",help="names of the images to be pulled");
                imagesName=self.parser.parse_args(commandLine.split()).imagesName;
                self.imageManager.pullImages(imagesName);
                
            return True;
                
        #if used volumes command line
        elif op=="volumes":
            self.parser.add_argument("concrete operation",type=str,nargs="?",help="the concrete operation to be executed by imagesManager");
            more_1_op=self.getSpecifiedArg(commandLine,1);
            if str(more_1_op)=="create":
                self.parser.add_argument("numberOfVolumesbeingCreated",type=int,help="number of volumes being created",nargs="?");
                numberOfVolumesCreating=self.parser.parse_args(commandLine.split()).numberOfVolumesbeingCreated;
                self.volumeManager.createVolume(numberOfVolumes=numberOfVolumesCreating);
            elif str(more_1_op)=="remove":
                self.parser.add_argument("removingVolumesNamesOrIds",type=str,nargs="*",help="names or ids of volumes to be removed");
                volumesNameOrId=self.parser.parse_args(commandLine.split()).removingVolumesNamesOrIds;
                self.volumeManager.removeVolumes(volumesNameOrId);
            elif str(more_1_op)=="list":
                self.volumeManager.showVolumes();
                
            return True;
        
        elif (op=="parallelproject") | (op=="pp"):
            self.parser.add_argument("numberOfNewContainers",type=int,nargs="?",help="number of new containers");
            self.parser.add_argument("dataPath",type=str,nargs="?",help="path to the data");
            self.parser.add_argument("scriptPath",type=str,nargs="?",help="path to the script");
            
            args=self.parser.parse_args(commandLine.split());
            numberOfnewContainers=args.numberOfNewContainers;
            dataPath=args.dataPath;
            scriptPath=args.scriptPath;
            results=self.ParallelProject(dataPath=dataPath,usedContainersAmount=numberOfnewContainers,
                                         usedPythonScriptPath=scriptPath);
            with open("parallel_project"+str(self.containerNameId)+".dat","wb") as file:
                bi_results=b''.join(results)
                file.write(bi_results);
            
            for i in results:
                print(i);
                
            return True;
                
                            
        elif op=="help":
            utils.printHelp.printHelp(self.helpTextPath);
            
            return True;

        elif op=="exit":
            return False;
        #if to do a project
        #elif op==self.choices[6]:
        
        else:
            print("the command is not existed, type 'help' for help");
            return True;
            
        
        