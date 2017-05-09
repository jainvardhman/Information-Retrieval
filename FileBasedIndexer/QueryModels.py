
//Hi we are collaboaratin here
import os
import math
import time
import re
from snowballstemmer import english_stemmer
from collections import OrderedDict
from elasticsearch import Elasticsearch
strBasePath = "C:\\Users\\Vardhman\\Downloads\\AP89_DATA\\AP_DATA";
outFolderName = "output";
filename = "query_desc.51-100.short.txt"
ignoreWordsFileName = "stoplist.txt"
ignoreWordsList = []
okapiOutput = "okapi.txt";
tfidfOutput = "tfidf.txt";
okapibm25Output = "okapibm25.txt";
unigramLaplaceOutput = "unigramLaplace.txt";
jelinekMercerOutput = "jelinekMercer.txt";
punct = [' ','.',',','"']
qtToDoc = {}
qtToQno = {}
qNoToQt = {}
docTermStats = {}
docToLength = {}
avgCorpusLength = 0
totalDocCount = 0
avgSet = False
#ps =PorterStemmer.PorterStemmer()
k1 = 1.2
k2 = 100
b = 0.75
vocabSize = 0
lambdaa = 0.5
stemmer = english_stemmer.EnglishStemmer()

def trimCharacters(term):
    for c in punct:
        term = re.sub('[.,"`~]','',term) #term.rstrip(c).rstrip(c)
    return (term.lower())

def readQueryAndMap():
    global ignoreWordsList
    ignoreWordsFile = open(strBasePath + "\\" + ignoreWordsFileName,"r+")
    ignoreWordsList = ignoreWordsFile.read().splitlines()
    ignoreWordsFile.close()

    fileRead = open(strBasePath + "\\" + filename,"r+")
    fileLines = fileRead.readlines()
    fileRead.close()
    for line in fileLines:
        queryTerms = line.split()
        if len(queryTerms) > 1:
            qno = trimCharacters(queryTerms[0])
            queryTerms[0] = trimCharacters(queryTerms[0])
            queryTerms = queryTerms[4:]
            queryTerms = list (set(queryTerms) - set(ignoreWordsList))
            formattedLine = ""
            for qt in queryTerms:
                if (qt != qno):
                    trimqt = trimCharacters(qt)
                    stemQt = stemmer._stem_word(trimqt)
                    formattedLine = formattedLine + stemQt + " "
                    if len(qtToQno):
                        if stemQt in qtToQno.keys():
                            qtToQno[stemQt] = qtToQno[stemQt] + " " + qno
                        else:
                            qtToQno[stemQt] = qno
                    else:
                        qtToQno[stemQt] = qno
            qNoToQt[qno] = formattedLine
            #print(qNoToQt[qno])


def getFieldStatistics():
    global avgCorpusLength
    global  totalDocCount
    keys = qtToQno.keys()
    i=0
    es = Elasticsearch()
    for key in keys:
        if i > 0:
            break;
        else:
            results = es.search(index='ap_dataset', doc_type="document", body={"query": {"match": {"TEXT": "'"+key +"'"}}})
            fs = es.termvector(index='ap_dataset', doc_type="document",id= results['hits']['hits'][0]['_id'],
                                                                 term_statistics = True)
            if (avgCorpusLength == 0):
                            fstats = fs['term_vectors']['TEXT']['field_statistics']
                            avgCorpusLength = fstats['sum_ttf'] / fstats['doc_count']
                            totalDocCount = fstats['doc_count']
        i= i+1
    print(avgCorpusLength)
    print(totalDocCount)

def getTermStatistics():
    startTime = time.time()
    es = Elasticsearch()
    for term in qtToQno.keys():
        qtDocList= []
        results = es.search(index='ap_dataset', doc_type="document", body={"query": {"match": {"TEXT": "'"+term +"'"}}}
        ,size=9000)
        for doc in results['hits']['hits'] :
            dictToAddInDStats = {}
            #print(doc["_id"])
            qtDocList.append(doc["_id"])
            if doc['_id'] in docTermStats.keys():
                continue
            else:
                docToLength[doc['_id']] = len(set(es.get(index='ap_dataset',doc_type="document",
                                                     id=doc['_id'])["_source"]["TEXT"].split()) - set(ignoreWordsList))
                ts = es.termvector(index='ap_dataset', doc_type="document",id= doc['_id'],
                                                         term_statistics = True,field_statistics = False)
                keysToKeep = set(qtToQno.keys()) & set(ts["term_vectors"]["TEXT"]["terms"].keys())
                #print (keysToKeep)
                for tKeys in keysToKeep:
                    dictToAddInDStats[tKeys] = ts["term_vectors"]["TEXT"]["terms"][tKeys]
                docTermStats[doc['_id']] = dictToAddInDStats
                print(len(docTermStats))
        qtToDoc[term] = qtDocList
    elapsedTime= time.time() - startTime
    #print(elapsedTime)
    #print(docTermStats)


def okapitfTermDoc(termfq,lenDoc):
        okapitf = termfq / (termfq + 0.5 + ((1.5) * lenDoc/avgCorpusLength))
        return okapitf

def tfidfTermDoc(termfq,docfq,lenDoc):
    tfidf = (termfq / (termfq + 0.5 + ((1.5) * lenDoc/avgCorpusLength)))*(math.log(totalDocCount/docfq))
    return  tfidf

def okapibm25(termfqd,termfqq,docfq,lenDoc):
    okapibm25 =  (math.log((totalDocCount + 0.5)/(docfq + 0.5))) \
             * ((termfqd + (k1 * termfqd))/ (termfqd + (k1 * ((1-b) + (b*(lenDoc/avgCorpusLength)))))) \
             * ((termfqq + (k2 * termfqq))/(termfqq + k2))
    return  okapibm25

def unigramlaplace(termfqd,lenDoc):
    unigramLaplace = (termfqd + 1) / (lenDoc + vocabSize)
    return  unigramLaplace

def jelinekmercer(termfqd,ttf,lenDoc):
    jelinekMercer = (lambdaa * (termfqd/lenDoc)) + ((1-lambdaa)* (ttf/vocabSize))
    return  jelinekMercer

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
                file.write("%s Q0 %s %d %f Exp \n" % (key,tup[0],i,tup[1]))
            else:
                break
            i+=1
    file.close()


def ModelWrapper(modelname):
    keys = qNoToQt.keys()
    queryDocScoreMapping={}
    outFileName = ""
    for key in keys:
        qtArray = getTermsFromString(qNoToQt[key])
        for docId in docToLength:
            termsOccured =[]
            ScoreQueryDoc = 0
            for term in qtArray:
                termCount = qtArray.count(term)
                #print(termCount)
                ScoreTerm= 0
                if term not in termsOccured:
                    termsOccured.append(term)
                    if term in docTermStats[docId].keys():
                        termfq = docTermStats[docId][term]["term_freq"]
                        doc_freq = docTermStats[docId][term]["doc_freq"]
                        lenDoc = docToLength[docId]
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
                    if key in queryDocScoreMapping.keys():
                        queryDocScoreMapping[key].append([docId,ScoreQueryDoc])
                    else:
                        queryDocScoreMapping[key] = []
                        queryDocScoreMapping[key].append([docId,ScoreQueryDoc])
    showResults(queryDocScoreMapping,outFileName)


def ModelWrapperLanguage(modelname):
    keys = qNoToQt.keys()
    queryDocScoreMapping={}
    outFileName = ""
    for key in keys:
        distinctDocID = []
        qtArray = getTermsFromString(qNoToQt[key])
        for qterm in qtArray:
            distinctDocID = list(set(distinctDocID + qtToDoc[qterm]))
        #print(distinctDocID)
        for docId in docToLength:
            termsOccured =[]
            ScoreQueryDoc = 0
            for term in qtArray:
                termCount = qtArray.count(term)
                #print(termCount)
                ScoreTerm= 0
                executeLaplace = False
                if term not in termsOccured:
                    total_term_freq=0
                    termsOccured.append(term)
                    if term in docTermStats[docId].keys():
                        termfq = docTermStats[docId][term]["term_freq"]
                        doc_freq = docTermStats[docId][term]["doc_freq"]
                        total_term_freq = docTermStats[docId][term]["ttf"]
                    else:
                        termfq = 0
                    #total_term_freq=0
                    #if qtToDoc[term]:
                    #    print(term)
                    #    if term in docTermStats[qtToDoc[term][0]].keys():
                    #        total_term_freq = docTermStats[qtToDoc[term][0]][term]["ttf"]
                    lenDoc = docToLength[docId]
                    if modelname.lower() == "unigramlaplace":
                        outFileName = unigramLaplaceOutput
                        ScoreTerm = ScoreTerm + unigramlaplace(termfq,lenDoc)
                    if modelname.lower() == "jelinekmercer": # In this case I am not able to get ttf for lot of terms because of
                        outFileName = jelinekMercerOutput    # mismatch in stemming.Not able to fix this
                        ScoreTerm = ScoreTerm + jelinekmercer(termfq,total_term_freq,lenDoc)
                    ScoreQueryDoc = ScoreQueryDoc + ScoreTerm
            if (ScoreQueryDoc > 0):
                    if key in queryDocScoreMapping.keys():
                        queryDocScoreMapping[key].append([docId,ScoreQueryDoc])
                    else:
                        queryDocScoreMapping[key] = []
                        queryDocScoreMapping[key].append([docId,ScoreQueryDoc])
    showResults(queryDocScoreMapping,outFileName)




def getTermsFromString(line):
    return (trimCharacters(line).split())

def getVocabularySize():
    global  vocabSize
    es = Elasticsearch()
    vocabOb = es.search(index='ap_dataset', doc_type="document", body={"aggs": {
                                                                "unique_terms":{
                                                                    "cardinality": {
                                                                            "field": "TEXT"
                                                                         }
                                                                    }
                                                                }})
    vocabSize = vocabOb["aggregations"]["unique_terms"]["value"]

def main():
    readQueryAndMap()
    getFieldStatistics()
    getTermStatistics()
    getVocabularySize()
    ModelWrapper("okapi")
    ModelWrapper("tfidf")
    ModelWrapper("okapibm25")
    ModelWrapperLanguage("unigramlaplace")
    ModelWrapperLanguage("jelinekmercer")
main()


