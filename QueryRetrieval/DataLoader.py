import os
import re
from elasticsearch import Elasticsearch
from os import path
strBasePath = "C:\\Users\\Vardhman\\Downloads\\AP89_DATA\\AP_DATA\\ap89_collection";
es = Elasticsearch()
baseDir = os.listdir(strBasePath)
myList = []
regexStr = "<DOC>.*?<(DOCNO)>([AP\\d\\-\\s]*)?</DOCNO>.*?<(TEXT)>(.*?)</TEXT>.*?</DOC>"
regex = re.compile(regexStr,re.DOTALL)

es.indices.create(index='documentCollection',ignore= 400,body="")
for filename in baseDir:
        if(filename.startswith("ap")):
            fileRead = open(strBasePath + "\\" + filename,"r+")
            fileContent = fileRead.read()
            fileContent = fileContent.replace("\n"," ")
            variable= regex.findall(fileContent)
            for i in range(0,len(variable)):
                myDict = {}
                myDict[str(variable[i][0])] = str(variable[i][1]).lstrip(' ').rstrip(' ')
                myDict[variable[i][2]] = str(variable[i][3])
                myList.append(myDict)
                es.index(index='ap_dataset',doc_type="document",id= myDict["DOCNO"],
                         body= myDict)
        else:
            "Filename is not in sync"


#f = open(strBasePath +"\\" + "output.txt", "a")
#f.write(str(myList))