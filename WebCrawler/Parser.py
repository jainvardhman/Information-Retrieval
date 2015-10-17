from bs4 import BeautifulSoup
import re
import json
import os
import re
from elasticsearch import Elasticsearch
from os import path
from Utilities import Document
FL_OUT_LINK = "outlinks.json"
FL_IN_LINK = "inlinks.json"

IN_LINKS_MAP = {}
OUT_LINKS_MAP = {}
strBasePath = "C:\\Users\\Vardhman\\Desktop\\outputFiles"
strDocsPath = strBasePath + "\\" + "docs"
baseDir = os.listdir(strDocsPath)

def main():
    fillLinkMaps()
    es = Elasticsearch()
    for filename in baseDir:
            if(filename.startswith("docs")):
                print(filename)
                fileRead = open(strDocsPath + "\\" + filename,"rb")
                fileContent = fileRead.read().decode("utf-8")
                fileContent = fileContent.replace("\n"," ")
                soup = BeautifulSoup(fileContent)
                docs = soup.find_all('doc')
                for dc in docs:
                    docOb = getDocOb(dc)
                    es.index(index='climate_1',doc_type="document",id= docOb["docno"],body= docOb)
            else:
                "Filename is not in sync"


def fillLinkMaps():
    global IN_LINKS_MAP
    global OUT_LINKS_MAP

    f = open(strBasePath + "\\" + FL_IN_LINK , "r")
    IN_LINKS_MAP = json.load(f)
    f.close()

    f = open(strBasePath + "\\" + FL_OUT_LINK , "r")
    OUT_LINKS_MAP = json.load(f)
    f.close()

def getDocOb(dcSoup):
    docno = dcSoup.find('docno')

    if not docno == None:
        docno = docno.text

    head = dcSoup.find('head')
    if not head == None:
        head = head.text

    text = dcSoup.find('text')
    if not text == None:
        text = text.text

    rawhtml = dcSoup.find('rawhtml')
    if not rawhtml == None:
        rawhtml = rawhtml.text.replace("\n"," ")

    headers = dcSoup.find('headers')
    if not headers == None:
        headers = headers.text

    inlinks = []
    outlinks = []

    if docno in  IN_LINKS_MAP.keys():
        print("found inlinks")
        inlinks = IN_LINKS_MAP[docno]

    if docno in  OUT_LINKS_MAP.keys():
        print("found outlinks")
        outlinks = OUT_LINKS_MAP[docno]

    docOb = {"docno":docno,"head" : head, "text" : text, "rawhtml" : rawhtml,
              "headers" : headers , "inlinks" : ",".join(IN_LINKS_MAP) , "outlinks" : ",".join(OUT_LINKS_MAP)}# Document(docno,head,text,rawhtml,headers,str(inlinks),str(outlinks))
    return docOb

main()