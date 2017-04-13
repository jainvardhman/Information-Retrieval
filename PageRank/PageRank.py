__author__ = 'Vardhman'
//this is for test also testing from dev  
import math

INPUT_PATH = "C:\\Vardhman-Drive\\Courses\\Information-Retrieval\\ir-assgn-4"
INPUT_FILE = "wt2g_inlinks.txt"
OUTPUT_FILE = "page_rank_output.txt"
OUTLINK_DICT = {}
INLINK_DICT = {}
PAGE_RANK = {}
ALL_LINKS = []
MATRIX = [[]]
INITIAL_PR = 1
EPS = 0.00001
PR_ITR=1

def fillOutLinks():
    for link in INLINK_DICT.keys():
        for inlink in INLINK_DICT[link]:
            if(hashEmptyOrkeyNotExist(OUTLINK_DICT,inlink)):
                OUTLINK_DICT[inlink] = [link]
            else:
                OUTLINK_DICT[inlink].append(link)

def fillInLinks():
    global INLINK_DICT
    cnt =0
    with open(INPUT_PATH + "\\" + INPUT_FILE,"r") as in_file:
        for line in in_file:
            cnt = cnt + 1
            lineArr =  line.rstrip("\n").rstrip(" ").split(" ")
            if (len(lineArr) > 1):
                for i in range(1,len(lineArr)):
                    if(hashEmptyOrkeyNotExist(INLINK_DICT,lineArr[0])):
                        INLINK_DICT[lineArr[0]] = [lineArr[i]]
                    else:
                        INLINK_DICT[lineArr[0]].append(lineArr[i])
            else:
                INLINK_DICT[lineArr[0]] = []
        print(cnt)
    in_file.close()


def hashEmptyOrkeyNotExist(hasht,key):
    return ((not bool(hasht)) or  (not (hasht.__contains__(key))))


def main():
    #fillOutLinks()
    fillInLinks()
    fillOutLinks()
    fillPageRanks()
    print(len(INLINK_DICT))
    print(len(OUTLINK_DICT))
    page_rank()
    outputFile()


def fillPageRanks():
    for link in INLINK_DICT.keys():
        PAGE_RANK[link] = INITIAL_PR

def page_rank():
    converge_count = 0
    itr = 1

    convergence = False
    while(not convergence):
        converge_count = 0
        print("pr_itr : " + str(itr))
        for link in PAGE_RANK:
            pr = 0
            #if(len(INLINK_DICT[link])>0):
            pr = 0.15 + 0.85 * (page_rank_inlinks(link))
            #else:
            #    pr = PAGE_RANK[link]
            if (abs(PAGE_RANK[link] - pr) <= EPS):
                converge_count = converge_count + 1
            PAGE_RANK[link] = pr
        print("conv count: " + str(converge_count))
        if(converge_count == len(PAGE_RANK)):
            convergence = True



def page_rank_inlinks(link):
    pr_inlinks = 0
    if(len(INLINK_DICT[link])>0):
        for inlink in INLINK_DICT[link]:
            pr_inlinks = pr_inlinks + (PAGE_RANK[inlink]/len(OUTLINK_DICT[inlink]))

    return pr_inlinks

def outputFile():
    global PAGE_RANK
    pg_sorted = sorted(PAGE_RANK.items(), key=lambda x:x[1], reverse=True)
    f = open(INPUT_PATH + "\\" + OUTPUT_FILE,"w")
    for link in pg_sorted:
        f.write(str(link[0]) + " " + str(link[1]) + "\n")
    f.close()

main()
