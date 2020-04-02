__author__ = 'Vardhman'
import sys
import os.path
import math
import  os
from Utilities import CommandArguments
QREL_PATH = ""
RANKING_FILE_PATH = ""
QUERY_MODE = False
QREL_MAP = {}
RANK_MAP = {}
VAL_AT_ARRAY = [5,10,20,50,100]
VAL_TYPE = ["P_AT_K","R_AT_K","F_AT_K","NDCG","AVG_PRECISION","R_PRECISION"]
PREC_AT_AVG = {}
REC_AT_AVG = {}//farzi commit
F1_AT_AVG = {}

def main():
    cmdArgs = getCommandParameters()
    if isinstance(cmdArgs, str):
        print(cmdArgs)
    else:
        print(cmdArgs.qrel_file)
        print(cmdArgs.rank_file)
        processQrel(cmdArgs)


def processQrel(cmdArgs):
    print(cmdArgs.qrel_file)
    with open(cmdArgs.qrel_file,"r") as q_file:
        for line in q_file:
            lineArr = line.split()
            if(hashEmptyOrkeyNotExist(QREL_MAP,lineArr[0])):
                QREL_MAP[lineArr[0]] = getQrelDict(lineArr)
            else:
                if(hashEmptyOrkeyNotExist(QREL_MAP[lineArr[0]],lineArr[2])):
                    QREL_MAP[lineArr[0]][lineArr[2]] = [lineArr[1],int(lineArr[3].rstrip("\n")),
                                                        int(lineArr[4].rstrip("\n")),
                                                        int(lineArr[5].rstrip("\n"))]
    q_file.close()

    with open(cmdArgs.rank_file,"r") as r_file:
        for line in r_file:
            lineArr = line.split()
            if(hashEmptyOrkeyNotExist(RANK_MAP,lineArr[0])):
                RANK_MAP[lineArr[0]] = getRankDict(lineArr)
            else:
                if(hashEmptyOrkeyNotExist(RANK_MAP[lineArr[0]],lineArr[2])):
                    RANK_MAP[lineArr[0]][lineArr[2]] = [int(lineArr[3]),lineArr[4].rstrip("\n")]
    r_file.close()

    for q_key in RANK_MAP.keys():
        #print(RANK_MAP[q_key].items())
        interimDict = {}
        #for key,value in sorted(RANK_MAP[q_key].items(), key=lambda kvt: kvt[1][1]):
        RANK_MAP[q_key] = sorted(RANK_MAP[q_key].items(), key=lambda kvt: kvt[1][0])
        #     interimDict[key] = value
        #RANK_MAP[q_key] = interimDict

    #print(RANK_MAP)
    print(QREL_MAP)
    print("haha")

    printOutput(cmdArgs.query_mode)

    #print(QREL_MAP)
    #print(RANK_MAP)
    #print(precisionatk(2000,"77"))
    #cnt = 0
    #sum_q_prec = 0
    #for q_key in RANK_MAP.keys():
    #    print(q_key + ":")
    #    print(str(precisionatk(10,q_key)))
    #    print(str(recallk(10,q_key)))
    #    print(str(fmeasurek(10,q_key)))
    #    print(str(rPrecision(q_key)))
    #    sum_q_prec = sum_q_prec + averagePrecision(q_key)
    #print(sum_q_prec/len(RANK_MAP.keys()))


def printOutput(queryMode):
    for q_key in RANK_MAP.keys():
        if queryMode == True:
            print("\nQuery Id = " + q_key + "\n")
        for val_t in VAL_TYPE:
            if val_t == "P_AT_K":
                if queryMode == True:
                    print("\nPrecision @:\n")
                for val_at in VAL_AT_ARRAY:
                    pre_this = round(precisionatk(val_at,q_key),4)
                    if queryMode == True:
                        print("at "+ str(val_at) + "  " + str(pre_this))
                    if (hashEmptyOrkeyNotExist(PREC_AT_AVG,val_at)):
                        PREC_AT_AVG[val_at] = [pre_this]
                    else:
                        PREC_AT_AVG[val_at].append(pre_this)
            if val_t == "R_AT_K":
                if queryMode == True:
                    print("\nRecall @:\n")
                for val_at in VAL_AT_ARRAY:
                    rec_this = round(recallk(val_at,q_key),4)
                    if queryMode == True:
                        print("at "+ str(val_at) + "  " + str(rec_this))
                    if (hashEmptyOrkeyNotExist(REC_AT_AVG,val_at)):
                        REC_AT_AVG[val_at] = [rec_this]
                    else:
                        REC_AT_AVG[val_at].append(rec_this)
            if val_t == "F_AT_K":
                if queryMode == True:
                    print("\nF1 @:\n")
                for val_at in VAL_AT_ARRAY:
                    f1_this = round(fmeasurek(val_at,q_key),4)
                    if queryMode == True:
                        print("at "+ str(val_at) + "  " + str(f1_this))
                    if (hashEmptyOrkeyNotExist(F1_AT_AVG,val_at)):
                        F1_AT_AVG[val_at] = [f1_this]
                    else:
                        F1_AT_AVG[val_at].append(f1_this)
            if val_t == "AVG_PRECISION":
                av_prec,q_mat = averagePrecision(q_key)
                if queryMode == True:
                    print("\nAverage Precision :\n")
                    print(round(av_prec,4))
            if val_t == "R_PRECISION":
                r_prec,q_mat = rPrecision(q_key)
                if queryMode == True:
                    print("\nR Precision :\n")
                    print(round(r_prec,4))
            #if val_t == "NDCG":
            #    ndcg = ndcg(q_key)
            #    print("\nNDCG:\n")
            #    print(round(ndcg,4))

    avgPrecisionAll()
    RPrecisionAll()
    ndcgAll()
    avgsAtAll()
    #sum_q_prec = 0
    #sum_r_prec = 0
    #for q_key in RANK_MAP.keys():
    #    sum_q_prec = sum_q_prec + averagePrecision(q_key)
    #    sum_r_prec = sum_r_prec + rPrecision(q_key)

    #print ("R Precision over all queries : " + str(sum_r_prec/len(RANK_MAP.keys())) + "\n")


def avgsAtAll():

    rec_avg_all = 0
    f1_avg_all = 0
    print("\nPrecision @:\n")
    for key in sorted(PREC_AT_AVG):
        prec_avg_all = 0
        prec_avg_all = sum(PREC_AT_AVG[key])/len(RANK_MAP.keys())
        print("at "+ str(key) + "  " + str(round(prec_avg_all,4)))

    print("\nRecall @:\n")
    for key in sorted(REC_AT_AVG):
        rec_avg_all = 0
        rec_avg_all = sum(REC_AT_AVG[key])/len(RANK_MAP.keys())
        print("at "+ str(key) + "  " + str(round(rec_avg_all,4)))

    print("\nF1 @:\n")
    for key in sorted(F1_AT_AVG):
        f1_avg_all = 0
        f1_avg_all = sum(F1_AT_AVG[key])/len(RANK_MAP.keys())
        print("at "+ str(key) + "  " + str(round(f1_avg_all,4)))

def getRelevantDocsFromQrel(q_key):
    rel_docs = 0
    for d_key in QREL_MAP[q_key]:
        if QREL_MAP[q_key][d_key][1] > 0:
            rel_docs = rel_docs + 1
    return rel_docs

def getQrelDict(lineArr):
    return {lineArr[2] : [lineArr[1],int(lineArr[3].rstrip("\n")),
                         int(lineArr[4].rstrip("\n")),
                         int(lineArr[5].rstrip("\n"))]}

def getRankDict(lineArr):
    return {lineArr[2] : [int(lineArr[3]),lineArr[4].rstrip("\n")]}


def getCommandParameters():
    argLength = len(sys.argv)
    counter = 1
    q_path = ""
    r_path = ""
    q_mode = False
    if argLength < 3 or argLength > 4:
        return "Invalid argument count"
    else:
        for arg in sys.argv:
            if argLength == 4:
                if counter == 3:
                    if(arg != "-q"):
                        return "Invalid Query Mode"
                    else:
                        q_mode = True
                elif counter == 2 or counter == 4:
                    if os.path.isfile(arg):
                        if counter == 2:
                            q_path = arg
                        else:
                            r_path = arg
                    else:
                        return "Invalid file path"
            elif argLength == 3:
                if counter == 2 or counter == 3:
                    if os.path.isfile(arg):
                        if counter == 2:
                            q_path = arg
                        else:
                            r_path = arg
                    else:
                        return "Invalid file path"
            counter = counter + 1
        cmdArgs = CommandArguments(q_path,q_mode,r_path)
        return cmdArgs

def hashEmptyOrkeyNotExist(hasht,key):
    return ((not bool(hasht)) or  (not (hasht.__contains__(key))))


def rPrecision(q_key):
    #found = False
    #rPrec = 0
    EPS = 0.0001
    #for count in range(1,len(RANK_MAP[q_key])):
        #precK = precisionatk(count,q_key)
        #recK = recallk(count,q_key)
    relevant_count = 0
    doc_seen_count = 0
    rPrec = 0
    precK = 0
    recK = 0
    for tups in RANK_MAP[q_key]:
        doc_seen_count = doc_seen_count + 1
        if tups[0] in QREL_MAP[q_key].keys():
            if majority_relevance_from_tuple(QREL_MAP[q_key][tups[0]]) != 0:
                relevant_count = relevant_count + 1

        precK = (relevant_count * 1.0) / doc_seen_count
        recK = (relevant_count * 1.0) / getRelevantDocsFromQrel(q_key)

        if ((precK - recK) <= EPS):
            rPrec = precK
            break


    query_match = 0

    return rPrec ,query_match


def majority_relevance_from_tuple(tuple):
    rel_encountered = {}
    for x in range(1, len(tuple)):
        if hashEmptyOrkeyNotExist(rel_encountered,str(tuple[x])):
            rel_encountered[str(tuple[x])] = 1
        else:
            rel_encountered[str(tuple[x])] = rel_encountered[str(tuple[x])] + 1

    rel_encountered = sorted(rel_encountered.items(), key=lambda x:x[1],reverse=True)

    return int(rel_encountered[0][0])


def precisionatk(k,q_key):
    relevant_count = 0
    doc_seen_count = 0

    for tups in RANK_MAP[q_key]:
        doc_seen_count = doc_seen_count + 1
        if tups[0] in QREL_MAP[q_key].keys():
            if majority_relevance_from_tuple(QREL_MAP[q_key][tups[0]]) != 0:
                relevant_count = relevant_count + 1


        if(doc_seen_count == k):
            break

    return (relevant_count/doc_seen_count)


def recallk(k,q_key):
    relevant_count = 0
    doc_seen_count = 0
    for tups in RANK_MAP[q_key]:
        doc_seen_count = doc_seen_count + 1
        if tups[0] in QREL_MAP[q_key].keys():
            if majority_relevance_from_tuple(QREL_MAP[q_key][tups[0]]) != 0:
                relevant_count = relevant_count + 1

        if(doc_seen_count == k):
            break
    return ((relevant_count * 1.0 )/getRelevantDocsFromQrel(q_key))


def fmeasurek(k,q_key):
    precK = precisionatk(k,q_key)
    recallK = recallk(k,q_key)

    if(precK == 0 and recallK ==0):
        return 0
    else:
        f1K = 2* precK * recallK / (precK + recallK)
        return f1K


def avgPrecisionAll():
    total_queries_having_matches = 0
    sum_q_prec = 0
    for q_key in RANK_MAP.keys():
        avgPrec,query_match = averagePrecision(q_key)
        sum_q_prec = sum_q_prec + avgPrec
        total_queries_having_matches = total_queries_having_matches + query_match
        #sum_q_prec = sum_q_prec + averagePrecision(q_key)
    print ("Average Precision over all queries : " + str(round((sum_q_prec/len(RANK_MAP.keys())),4)) + "\n")


def RPrecisionAll():
    total_queries_having_matches = 0
    sum_q_prec = 0
    for q_key in RANK_MAP.keys():
        RPrec,query_match = rPrecision(q_key)
        sum_q_prec = sum_q_prec + RPrec
        total_queries_having_matches = total_queries_having_matches + query_match
        #sum_q_prec = sum_q_prec + averagePrecision(q_key)
    print ("R Precision over all queries : " + str(round((sum_q_prec/len(RANK_MAP.keys())),4)) + "\n")


def ndcgAll():
    sum_q_ndcg = 0
    for q_key in RANK_MAP.keys():
        avgNdcg = ndcg(q_key)
        sum_q_ndcg = sum_q_ndcg + avgNdcg
        #sum_q_prec = sum_q_prec + averagePrecision(q_key)
    print ("Average ndcg over all queries : " + str(round((sum_q_ndcg/len(RANK_MAP.keys())),4)) + "\n")

def averagePrecision(q_key):
    sum_precisions = 0
    relevant_count = 0
    doc_seen_count = 0
    for tups in RANK_MAP[q_key]:
        doc_seen_count = doc_seen_count + 1
        if tups[0] in QREL_MAP[q_key].keys():
            if majority_relevance_from_tuple(QREL_MAP[q_key][tups[0]]) != 0:
                relevant_count = relevant_count + 1
                sum_precisions = sum_precisions + (relevant_count / doc_seen_count)

    if relevant_count > 0:
       query_match =  1
    else:
        query_match = 0
    return (sum_precisions/getRelevantDocsFromQrel(q_key)),query_match


def ndcg(q_key):
    doc_seen_count= 0
    dcg = 0
    dcgSorted = 0
    listScores = []
    for tups in RANK_MAP[q_key]:
        doc_seen_count = doc_seen_count + 1
        if tups[0] in QREL_MAP[q_key].keys():
            crnt_score = int(QREL_MAP[q_key][tups[0]][1])
            listScores.append(int(QREL_MAP[q_key][tups[0]][1]))
            if(doc_seen_count > 1):
                crnt_score = crnt_score / math.log(doc_seen_count,2)
            dcg = dcg + crnt_score

    listScores.sort(reverse=True)
    dc_Count = 0
    for score in listScores:
        dc_Count = dc_Count + 1
        crnt_score_n = score
        if(dc_Count > 1):
            crnt_score_n = crnt_score_n / math.log(dc_Count,2)
        dcgSorted = dcgSorted + crnt_score_n

    if (dcgSorted == 0):
        ndcg = 0
    else:
        ndcg = dcg/dcgSorted

    return ndcg


main()
