__author__ = 'Vardhman'


import urllib.request
import urllib.response
from bs4 import BeautifulSoup
from Utilities import PageURLsMap,UrlStateMap,FrontierWrapper,PageContentAndHeaders
from urllib.parse import urlsplit,urlparse,urlunparse,quote,unquote
from datetime import  datetime
from datetime import  timedelta
import time
import re
import json
import Canonicalizer
import socket
DOMAIN_LAST_HIT = {}
ALL_LINKS_VISITED = []
IN_LINK_MAP ={}
OUT_LINK_MAP ={}
DOCS_PER_FILE = 50
DOC_FILE_NAME = "docs_output_"
DOC_FOLDER = "docs"
OUT_PATH = "C:\\Users\\Vardhman\\Desktop\\outputFiles"
FL_OUT_LINK = "outlinks.json"
FL_IN_LINK = "inlinks.json"

# put a check here that info should always have content type = text/html else dont crawl that link
#--f = urllib.request.urlopen("http://money.cnn.com/2015/03/10/news/companies/dunkin-donuts-titanium-dioxide/")

#gets the header data and extracts content-type
#--headers = f.info()
#--print(headers)
#--print(headers["Content-Type"])

#reads the response using beautiful soup
#--soup = BeautifulSoup(f.read())

#prints pretty html
#print(soup.prettify())

#finds all a tags and extracts all urls from it
#for link in soup.find_all('a'):
#    print(link.get('href'))
# if the urlsdont have any domain name when canonicalization is done,
# add the current domain to the list

#finds all p tags and extracts all text from it
#paras = soup.find_all('p')
#for para in paras:
#    print(para.text)

#does not look very useful yet
#print(soup.get_text())


def init_frontier(frontier,c_level):
    lst_url_state_map = []
    lst_page_urls_map = []
    lst_seed_urls = ["http://www.reuters.com/article/2015/03/18/us-catholics-climate-idUSKBN0ME25U20150318",
                     "http://en.wikipedia.org/wiki/Climate_change",
                     "http://www.thedailybeast.com/articles/2015/03/18/the-right-warms-up-to-climate-change.html",
                     "http://www.washingtonpost.com/blogs/erik-wemple/wp/2015/03/17/npr-ombudsman-equivocates-over-equivalence-story-on-climate-change-fight/",
                     "http://thinkprogress.org/climate/2015/03/18/3635376/ted-cruz-climate-isnt-changing/",
                     "http://www.theverge.com/2015/3/18/8213595/google-trekker-helping-map-climate-change",
                     "http://news.discovery.com/earth/global-warming/add-climate-change-in-disaster-planning-fema-urges-150318.htm",
                     "http://www.washingtonpost.com/blogs/the-fix/wp/2015/03/17/the-gop-house-budget-calls-dod-climate-research-waste-dod-calls-climate-change-an-immediate-risk/",
                     "http://www.washingtonpost.com/blogs/fact-checker/wp/2015/03/18/kerrys-claim-that-he-organized-the-very-first-hearings-on-climate-change/",
                     "http://www.weather.com/science/environment/news/climate-change-decrease-food-quality-australia-new-study",
                     "http://www.washingtonpost.com/blogs/capital-weather-gang/wp/2015/03/18/top-hurricane-expert-climate-change-influenced-tropical-cyclone-pam/",
                     "http://www.nasa.gov/mission_pages/noaa-n/climate/climate_weather.html#.VP9bRyklBYw",
                     "https://nsidc.org/cryosphere/arctic-meteorology/climate_vs_weather.html",
                     "http://en.wikipedia.org/wiki/Weather_and_climate"]

    for i in range(len(lst_seed_urls)):
        lst_url_state_map.append(lst_seed_urls[i])

    lst_page_urls_map.append(PageURLsMap("seeds",lst_url_state_map,""))
    frontier[c_level] = lst_page_urls_map
    return frontier


def main():
    frontier = {}
    current_level = 0
    docs_for_file = 0
    fileCount = 0
    frontier = init_frontier(frontier,current_level)
    frontier_wrapper = FrontierWrapper(frontier,current_level)
    frontier_wrapper = go_crawl(frontier_wrapper,docs_for_file,fileCount)

    #print(ALL_LINKS_VISITED)
    #print(IN_LINK_MAP)
    dumpInLinks()
    #print("last level " + str(frontier_wrapper.current_level))



def go_crawl(frontier_wrapper,docs_for_file,docFileCount):
    global ALL_LINKS_VISITED
    terminate = False
    priority_queue = {}
    for pgurlmap in frontier_wrapper.frontier[frontier_wrapper.current_level]:
        #print("length of all pgurlmap " + str(pgurlmap.page) + ": " + str(len(pgurlmap.lst_urlstate)))
        for urlstmp in pgurlmap.lst_urlstate:
            #if  urlstmp.visited == False and (not ALL_LINKS_VISITED.__contains__(urlstmp.url)):
            if  (not ALL_LINKS_VISITED.__contains__(urlstmp)):
                if(hashEmptyOrkeyNotExist(priority_queue,urlstmp)):
                    priority_queue[urlstmp] = 1
                else:
                    priority_queue[urlstmp] = priority_queue[urlstmp] + 1

            if(hashEmptyOrkeyNotExist(IN_LINK_MAP,urlstmp)):
                IN_LINK_MAP[urlstmp] = [pgurlmap.page]
            else:
                IN_LINK_MAP[urlstmp].append(pgurlmap.page)

            if(hashEmptyOrkeyNotExist(OUT_LINK_MAP,pgurlmap.page)):
                OUT_LINK_MAP[pgurlmap.page] = [urlstmp]
            else:
                OUT_LINK_MAP[pgurlmap.page].append(urlstmp)

    #print(IN_LINK_MAP)
    priority_queue_sorted = sorted(priority_queue.items(), key= lambda x: x[1],reverse=True)
    current_count = 0
    len_pq = len(priority_queue_sorted)
    for pq_item in priority_queue_sorted:
        if (current_count/len_pq > .75 and not frontier_wrapper.current_level == 0):
            break
        pgUrlMapFetched,docs_for_file,docFileCount = processUrl(pq_item[0],docs_for_file,docFileCount)
        if not pgUrlMapFetched == None:
            #current_count = current_count + 1
            frontier_wrapper.frontier = updateFrontier(frontier_wrapper.frontier,
                                                       frontier_wrapper.current_level,
                                                       pgUrlMapFetched)
            #outputLinkGraph(pgUrlMapFetched)
        #urlstmp.visited = True
        ALL_LINKS_VISITED.append(pq_item[0])
        print("length of all links: " + str(len(ALL_LINKS_VISITED)))
        #print("current level: " + str(frontier_wrapper.current_level))
        #print("frontier length: " + str(len(frontier_wrapper.frontier)))
        terminate = checkTermination()
        current_count = current_count + 1
            #else:
            #    urlstmp.visited = True
        if terminate:
            break
        if terminate:
            break
    if terminate:
        frontier_wrapper = FrontierWrapper(frontier_wrapper.frontier,frontier_wrapper.current_level+1)
        return frontier_wrapper
    else:
        #print("updating frontier")
        frontier_wrapper = FrontierWrapper(removeFrontierPrevLevel(frontier_wrapper.frontier,frontier_wrapper.current_level)
                                           ,frontier_wrapper.current_level+1)
        #del frontier_wrapper.frontier[frontier_wrapper.current_level-1]
        go_crawl(frontier_wrapper,docs_for_file,docFileCount)

def removeFrontierPrevLevel(frontier,level):
    frontier[level] = None
    return frontier


def outputLinkGraph(pgURLMap):
    encoding = "iso-8859-1"
    if not pgURLMap.encoding == "":
        encoding = pgURLMap.encoding
    f = open(OUT_PATH + "\\" + FL_OUT_LINK , "a", encoding = encoding)
    f.write(pgURLMap.page + "\t")
    for urlstmp in pgURLMap.lst_urlstate:
        #print(urlstmp)
        try:
            f.write(urlstmp + "\t")
        except Exception as excp:
            continue
    f.write("\n")
    f.close()


def checkTermination():
    global  ALL_LINKS_VISITED
    if(len(ALL_LINKS_VISITED) >=15000):
        return True
    else:
        return False

def updateFrontier(frontier,current_level,pgUrlMapFetched):
    #frontier[current_level] = None
    if(hashEmptyOrkeyNotExist(frontier,current_level+1)):
        frontier[current_level+1] = [pgUrlMapFetched]
    else:
        frontier[current_level+1].append(pgUrlMapFetched)
    return frontier

def hashEmptyOrkeyNotExist(hasht,key):
    return ((not bool(hasht)) or  (not (hasht.__contains__(key))))

def getContTypeFromHeader(header):
    return header["Content-Type"]

def processUrl(url,docs_for_file,docFileCount):
    global  ALL_LINKS_VISITED
    if (not ALL_LINKS_VISITED.__contains__(url)):
        pgContandHdrs = fetchPage(url)
        if not pgContandHdrs == None:
            contType = getContTypeFromHeader(pgContandHdrs.headers)
            lst_urlstate = getAllLinks(pgContandHdrs.content,url,contType)
            if lst_urlstate == None:
                return None,docs_for_file,docFileCount
            content = ""
            if str(contType).__contains__("charset") and str(contType).__contains__("="):
                content = str(contType).split("=")[1]

            docs_for_file = docs_for_file + 1
            if docs_for_file > 50 :
                docs_for_file = 1
                docFileCount = docFileCount + 1
            written = writeDocsToFile(url,pgContandHdrs,docFileCount)

            if not written :
                if docs_for_file == 1:
                    if docFileCount >=1:
                        docs_for_file = 50
                        docFileCount = docFileCount - 1
                    else:
                        docs_for_file = 0
                else:
                    docs_for_file = docs_for_file - 1

            return PageURLsMap(url,lst_urlstate,content),docs_for_file,docFileCount
        else:
            return None,docs_for_file,docFileCount
    else:
        return None,docs_for_file,docFileCount


def writeDocsToFile(url,pgContandHdrs,docFileCount):
    try:
        contType = getContTypeFromHeader(pgContandHdrs.headers)
        soup = BeautifulSoup(pgContandHdrs.content)
        enc = "iso-8859-1"
        if str(contType).__contains__("charset") and str(contType).__contains__("="):
            enc = str(contType).split("=")[1]
        file = open(OUT_PATH + "\\" + DOC_FOLDER + "\\" + DOC_FILE_NAME + str(docFileCount) + ".txt","ab")
        cleanedText = soup.get_text()
        title = soup.find("title")
        if not title == None:
           title = title.text
        else:
            title = ""
        file.write(getDocStringEntityForFile(soup,url,cleanedText,title,str(pgContandHdrs.headers)).encode("utf-8"))
        file.close()
        return True
    except Exception as excp:
        #print(pgContandHdrs.headers["Content-Language"])
        print("exception in file write" + str(excp))
        file.close()
        return False

def dumpInLinks():
    f = open(OUT_PATH + "\\" + FL_IN_LINK , "w")
    json.dump(IN_LINK_MAP,indent= 1, fp=f)
    f.close()

    f = open(OUT_PATH + "\\" + FL_OUT_LINK , "w")
    json.dump(OUT_LINK_MAP,indent= 1, fp=f)
    f.close()

def getDocStringEntityForFile(soup,url,cleanedText,title,hdrs):
    outString = "<DOC>"
    outString = outString + "<DOCNO>"
    outString = outString + url
    outString = outString + "</DOCNO>"
    outString = outString + "<HEAD>"
    outString = outString + title
    outString = outString + "</HEAD>"
    outString = outString + "<TEXT>"
    outString = outString + re.sub("[ ]+"," ",cleanedText).replace("\n","")
    outString = outString + "</TEXT>"
    outString = outString + "<RAWHTML>"
    outString = outString + str(soup)
    outString = outString + "</RAWHTML>"
    outString = outString + "<HEADERS>"
    outString = outString + hdrs
    outString = outString + "</HEADERS>"
    outString = outString + "</DOC>"
    return  outString

def getAllLinks(pageContent,crawled_from_url,headers):
    try:
        lst_urlstate = []
        soup = BeautifulSoup(pageContent)
        anchorTags = soup.find_all('a')
        for aT in anchorTags:
            urlToProc = aT.get('href')
            if not urlToProc == None:
                #print("going to call can on " + str(urlToProc) + " " + str(crawled_from_url))
                canUrl = Canonicalizer.canonicalizeMain(urlToProc,crawled_from_url,headers)
                #if shouldAddUrl(canUrl):
                lst_urlstate.append(canUrl)
    except Exception as excp:
        return None

    return set(lst_urlstate)

def shouldAddUrl(f,url):
    global  ALL_LINKS_VISITED
    if (not ALL_LINKS_VISITED.__contains__(url)):
        contType = getContTypeFromHeader(fetchPageHeaders(f))
        if str(contType).__contains__("text/html"):
            return True
        else:
            return False
    else:
        return False

def fetchPage(url):
    f = fetchURLOpened(url)
    try:
        if not f == None:
            if (shouldAddUrl(f,url)):
                pageContent = f.read()
                headers = fetchPageHeaders(f)
                return  PageContentAndHeaders(pageContent,headers)
    except socket.gaierror:
        return None
    except Exception as excp:
        return None
    return None

def fetchPageHeaders(f):
    headers = f.info()
    return headers#["Content-Type"]

def fetchURLOpened(url):
    # add timing logic here
    urlParsed = urlparse(url)
    urlunparsed = getUnparsedUrlFromParsed(urlParsed)
    try:
        verifyLastCalledTime(urlParsed.netloc)
        addTimeForDomain(urlParsed.netloc)
        f = urllib.request.urlopen(urlunparsed)
        return f
    except Exception as excp:
        print("exception in opening url")
        return None

def getUnparsedUrlFromParsed(urlParsed):
    return urlunparse(urllib.parse.ParseResult(urlParsed.scheme,
                                        urlParsed.netloc,
                                        quote(urlParsed.path),
                                        urlParsed.params,
                                        urlParsed.query,
                                        urlParsed.fragment))

def verifyLastCalledTime(netloc):
    global DOMAIN_LAST_HIT
    #print("domain being hit: " + netloc)
    if hashEmptyOrkeyNotExist(DOMAIN_LAST_HIT,netloc):
        DOMAIN_LAST_HIT[netloc] = datetime.now()
    elif netloc in DOMAIN_LAST_HIT.keys():
        current_time = datetime.now()
        new_time = DOMAIN_LAST_HIT[netloc] + timedelta(seconds=1)
        #print((new_time-current_time).microseconds)
        if current_time < new_time:
            print("sleeping")
            time.sleep((new_time-current_time).microseconds/1000000)


def addTimeForDomain(netloc):
    global DOMAIN_LAST_HIT
    if hashEmptyOrkeyNotExist(DOMAIN_LAST_HIT,netloc):
        DOMAIN_LAST_HIT[netloc] = datetime.now()

main()