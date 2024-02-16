def printHelp(helpTextPath):
    with open(helpTextPath,"r") as helpFile:
        line=" ";
        content="";
        while line!="":
            line=helpFile.read();
            content+=line;
        print(content);