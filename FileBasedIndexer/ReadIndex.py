import os
import re
import sys
import copy
import math
from Utilities import OffsetMap
from Utilities import DocumentBlock
from snowballstemmer import english_stemmer
qArray = ["forest", "ramachandran","pap","anticompetit"]


okapiOutput = "okapi.txt";
tfidfOutput = "tfidf.txt";
okapibm25Output = "okapibm25.txt";
unigramLaplaceOutput = "unigramLaplace.txt";
jelinekMercerOutput = "jelinekMercer.txt";
hashTokenNameId = {}
hashDocNameId = {}
hashGlobalFileOffset = {}
hashDocIdLength = {}
docTermStats = {}
termDocStats = {}
stopWords = []
punct = [' ','.',',','"']
strBasePath = "C:\\Users\\Vardhman\\Downloads\\AP89_DATA\\AP_DATA";
outPath = "C:\\Users\\Vardhman\\Downloads\\AP89_DATA\\AP_DATA\\hw2"
FL_OFFSETS =  "offset.txt"
FL_TOKEN_ID_MAP =  "tokenmap.txt"
FL_DOC_ID_MAP =  "docmap.txt"
FL_INVERTED_INDEX = "index.txt"
FL_DOC_WORD_COUNT = "termcount.txt"
FL_STOP_WORDS =  "stoplist.txt"
FL_QUERY_FILE = "query_desc.51-100.short.txt"
stemmer = english_stemmer.EnglishStemmer()
qtToDoc = {}
qtToQno = {}
qNoToQt = {}
docTermStats = {}
avgCorpusLength = 0
outFolderName = "output"
k1 = 1.2
k2 = 100
b = 0.75

def showResults(dict,outfilename):
    keys = dict.keys()
    outDirPath =  strBasePath + "\\" + outFolderName
    if not os.path.exists(outDirPath):
        os.makedirs(outDirPath)
    if os.path.isfile(outDirPath + "\\" + outfilename):
        os.remove(outDirPath + "\\" + outfilename)
    file = open(outDirPath + "\\" + outfilename, 'w')
    for key in keys:
        sortedDict = sorted(dict[key], key=lambda docum: docum[1],reverse=True)
        i = 1
        for tup in sortedDict:
            if i<=1000:
                file.write("%s Q0 %s %d %f Exp \n" % (key,hashDocNameId[tup[0]],i,tup[1]))
            else:
                break
            i+=1
    file.close()



def readQueryAndMap(mode):
    global stopWords
    ignoreWordsFile = open(strBasePath + "\\" + FL_STOP_WORDS,"r+")
    stopWords = ignoreWordsFile.read().splitlines()
    ignoreWordsFile.close()

    fileRead = open(strBasePath + "\\" + FL_QUERY_FILE,"r+")
    fileLines = fileRead.readlines()
    fileRead.close()
    for line in fileLines:
        queryTerms = getTokenizedText(line).split()
        if len(queryTerms) > 1:
            qno = trimCharacters(queryTerms[0])
            queryTerms[0] = trimCharacters(queryTerms[0])
            queryTerms = queryTerms[4:]
            queryTerms = filterTermsByMode(queryTerms,mode)# list (set(queryTerms) - set(stopWords))
            formattedLine = ""
            for qt in queryTerms:
                if (qt != qno):
#                    trimqt = trimCharacters(qt)
#                    stemQt = stemmer._stem_word(trimqt)
                    formattedLine = formattedLine + qt + " "
                    if len(qtToQno):
                        if qt in qtToQno.keys():
                            qtToQno[qt] = qtToQno[qt] + " " + qno
                        else:
                            qtToQno[qt] = qno
                    else:
                        qtToQno[qt] = qno
            qNoToQt[qno] = formattedLine

def getTokenizedText(parsedText):
    substituteText = re.sub("[-]", " ", parsedText)
    substituteText = re.sub("[^(\\s\\w+(\\.?\\-?\\w+)\\s)*]", "", substituteText)
    substituteText = re.sub("[\\(\\)_]", " ", substituteText)
    substituteText = re.sub("[\\.]+", ".", substituteText)
    substituteText = re.sub("[ ]+", " ", substituteText)
    substituteText = re.sub("(\\. )", " ", substituteText)
    substituteText = re.sub("(\\? )", " ", substituteText)
    return str.lower(substituteText)


def filterTermsByMode(termList,mode):
    if mode == "DEFAULT":
        return termList
    elif mode == "STOPONLY":
        return filterStopWords(termList)
    elif mode == "STEMONLY":
        return stemWords(termList)
    else: # STEMNSTOP
        tempList = filterStopWords(termList)
        return stemWords(tempList)

def filterStopWords(termList):
    return (set(termList) - set(stopWords))

def stemWords(termList):
    tempList = []
    for term in termList:
        tempList.append(stemmer._stem_word(term))
    return tempList

def trimCharacters(term):
    for c in punct:
        term = re.sub('[.,"`~]','',term) #term.rstrip(c).rstrip(c)
    return (term.lower())


def getQTermStats(qTerm,mode):
    fileII = open(outPath + "\\" + FL_INVERTED_INDEX ,"r+")
    #for qTerm in qArray:
    if(not (hashEmptyOrkeyNotExist(hashTokenNameId,qTerm))):
        offMap = hashGlobalFileOffset[str(hashTokenNameId[str(qTerm)])]
        fileII.seek(offMap.startPos)
        termII = fileII.readline(offMap.bytesToRead)
        return termII
    return ""
    #fileII.close()

def initHashes(mode):
        global hashTokenNameId
        global hashDocNameId
        global hashGlobalFileOffset
        global hashDocIdLength
        global FL_OFFSETS
        global FL_TOKEN_ID_MAP
        global FL_DOC_ID_MAP
        global FL_INVERTED_INDEX
        global FL_DOC_WORD_COUNT
        global avgCorpusLength

        FL_OFFSETS = mode + "_" + FL_OFFSETS
        FL_TOKEN_ID_MAP = mode + "_" + FL_TOKEN_ID_MAP
        FL_DOC_ID_MAP = mode + "_" + FL_DOC_ID_MAP
        FL_INVERTED_INDEX = mode + "_" + FL_INVERTED_INDEX
        FL_DOC_WORD_COUNT = mode + "_" + FL_DOC_WORD_COUNT
        fileOff = open(outPath + "\\" + FL_OFFSETS ,"r+")
        fileTok = open(outPath + "\\" + FL_TOKEN_ID_MAP ,"r+")
        fileDoc = open(outPath + "\\" + FL_DOC_ID_MAP ,"r+")
        fileDocLen = open(outPath + "\\" + FL_DOC_WORD_COUNT ,"r+")

        for line in fileOff:
            offset_row = line.split(" ")
            if(len(offset_row) >=3):
                hashGlobalFileOffset[offset_row[0]] = OffsetMap(int(offset_row[1]),int(offset_row[2].rstrip("\n")))

        for line in fileTok:
            tok_row = line.split(" ")
            if(len(tok_row) >=2):
                hashTokenNameId[tok_row[0]] = int(tok_row[1].rstrip("\n"))

        for line in fileDoc:
            doc_row = line.split(" ")
            if(len(doc_row) >=2):
                hashDocNameId[doc_row[1].rstrip("\n")] =  doc_row[0]

        for line in fileDocLen:
            doc_len_row = line.split(" ")
            if(len(doc_len_row) >=2):
                hashDocIdLength[doc_len_row[0]] =  int(doc_len_row[1].rstrip("\n"))
                avgCorpusLength = avgCorpusLength + hashDocIdLength[doc_len_row[0]]

        fileOff.close()
        fileTok.close()
        fileDoc.close()
        fileDocLen.close()

def hashEmptyOrkeyNotExist(hasht,key):
    return ((not bool(hasht)) or  (not (hasht.__contains__(key))))

def getTermStatistics(mode):
    for term in qtToQno.keys():
        addToDocTermStats(getQTermStats(term,mode))

    fileDT = open(outPath + "\\" + "dtstats.txt","w")
    fileDT.write(str(docTermStats))
    fileDT.close()

def getTermsFromString(line):
    return (trimCharacters(line).split())


def getDFOfaTerm(termii):
    #termii = getQTermStats(term,"")
    if(termii != ""):
        df = len(termii.rstrip("\n").rstrip(";").split(";"))
        return df
    return 0

def getTFOfaTermForDoc(termii,docId):
    #termii = getQTermStats(term,"")
    if(termii != ""):
        tf = getTFfromTermII(termii,docId)
        return tf
    return 0


def okapitfTermDoc(termfq,lenDoc):
        okapitf = termfq / (termfq + 0.5 + ((1.5) * lenDoc/avgCorpusLength))
        return okapitf

def ModelWrapper(modelname):
    keys = qNoToQt.keys()
    queryDocScoreMapping={}
    outFileName = ""
    print(len(docTermStats))
    for key in keys:
        qtArray = getTermsFromString(qNoToQt[key])
        for docId in docTermStats:
            #print("docid" + docId)
            termsOccured =[]
            ScoreQueryDoc = 0
            for term in qtArray:
                #print("term " + term)
                termCount = qtArray.count(term)
                #print(termCount)
                ScoreTerm= 0
                if term not in termsOccured:
                    termsOccured.append(term)
                    if (str(hashTokenNameId[term]) in docTermStats[docId].keys()):
                        termfq = len(termDocStats[str(hashTokenNameId[term])][docId])
                        doc_freq = len(termDocStats[str(hashTokenNameId[term])])
                        lenDoc = hashDocIdLength[docId]
                        if modelname.lower() == "okapi":
                            ScoreTerm = ScoreTerm + okapitfTermDoc(termfq,lenDoc)
                            outFileName = okapiOutput
                        elif modelname.lower() == "tfidf":
                            outFileName = tfidfOutput
                            ScoreTerm = ScoreTerm + tfidfTermDoc(termfq,doc_freq,lenDoc)
                        elif modelname.lower() == "okapibm25":
                            outFileName = okapibm25Output
                            ScoreTerm = ScoreTerm + okapibm25(termfq,termCount,doc_freq,lenDoc)
                        #elif modelname.lower() == "unigramlaplace":
                        #    outFileName = unigramLaplaceOutput
                        #    ScoreTerm = ScoreTerm + unigramlaplace(termfq,lenDoc)
                        #elif modelname.lower() == "jelinekmercer": # In this case I am not able to get ttf for lot of terms because of
                        #    outFileName = jelinekMercerOutput    # mismatch in stemming.Not able to fix this
                        #    ScoreTerm = ScoreTerm + jelinekmercer(termfq,total_term_freq,lenDoc)
                    ScoreQueryDoc = ScoreQueryDoc + ScoreTerm
            if (ScoreQueryDoc > 0):
                    #print(ScoreQueryDoc)
                    if key in queryDocScoreMapping.keys():
                        queryDocScoreMapping[key].append([docId,ScoreQueryDoc])
                    else:
                        queryDocScoreMapping[key] = []
                        queryDocScoreMapping[key].append([docId,ScoreQueryDoc])
    #print(queryDocScoreMapping)
    showResults(queryDocScoreMapping,outFileName)


def tfidfTermDoc(termfq,docfq,lenDoc):
    tfidf = (termfq / (termfq + 0.5 + ((1.5) * lenDoc/avgCorpusLength)))*(math.log(len(hashDocNameId)/docfq))
    return  tfidf


def okapibm25(termfqd,termfqq,docfq,lenDoc):
    okapibm25 =  (math.log((len(hashDocNameId) + 0.5)/(docfq + 0.5))) \
             * ((termfqd + (k1 * termfqd))/ (termfqd + (k1 * ((1-b) + (b*(lenDoc/avgCorpusLength)))))) \
             * ((termfqq + (k2 * termfqq))/(termfqq + k2))
    return  okapibm25

def getTFfromTermII(termii,docIdToMatch):
    colonSplit = termii.split(":")
    tf = 0
    if(len(colonSplit) >=2):
        tokenId = colonSplit[0]
        docBlocks = colonSplit[1].rstrip(";").rstrip("\n").split(";")

        for docBlock in docBlocks:
            hyphenSplit = docBlock.split("-")
            if(len(hyphenSplit)>=2 ):
                docId = hyphenSplit[0]
                posArr = hyphenSplit[1].lstrip(" ").rstrip(" ").split(" ")
                if (docId == docIdToMatch):
                    tf= len(posArr)
                    break
    return tf

def addToDocTermStats(termInvertedIndex):
    colonSplit = termInvertedIndex.split(":")
    if(len(colonSplit) >=2):
        tokenId = colonSplit[0]
        docBlocks = colonSplit[1].rstrip(";").rstrip("\n").split(";")

        for docBlock in docBlocks:
            hyphenSplit = docBlock.split("-")
            if(len(hyphenSplit)>=2 ):
                docId = hyphenSplit[0]
                posArr = hyphenSplit[1].lstrip(" ").rstrip(" ").split(" ")
                if(hashEmptyOrkeyNotExist(docTermStats,docId)):
                    docTermStats[docId] = {tokenId : posArr}
                else:
                    docTermStats[docId][tokenId] = posArr

                if(hashEmptyOrkeyNotExist(termDocStats,tokenId)):
                    termDocStats[tokenId] = { docId : posArr}
                else:
                    termDocStats[tokenId][docId] = posArr
def main():
    initHashes("STEMNSTOP")
    readQueryAndMap("STEMNSTOP")
    getTermStatistics("STEMNSTOP")
    ModelWrapper("okapi")
    ModelWrapper("tfidf")
    ModelWrapper("okapibm25")

main()