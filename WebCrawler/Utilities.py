__author__ = 'Vardhman'

class UrlStateMap(object):
    def __init__(self, url,visited):
        self.url = url
        self.visited = visited


class PageURLsMap(object):
    def __init__(self, page ,lst_urlstate,encoding):
        self.page = page
        self.lst_urlstate = lst_urlstate
        self.encoding = encoding

class FrontierWrapper(object):
    def __init__(self, frontier ,current_level):
        self.frontier = frontier
        self.current_level = current_level


class PageContentAndHeaders(object):
    def __init__(self, content,headers):
        self.content = content
        self.headers = headers

class Priority_Queue(object):
    def __init__(self, url,inCount):
        self.url = url
        self.inCount = inCount


class Document(object):
    def __init__(self, docno,head,text,rawhtml,headers,inlinks,outlinks):
        self.docno = docno
        self.head = head
        self.text = text
        self.rawhtml = rawhtml
        self.headers = headers
        self.inlinks = inlinks
        self.outlinks = outlinks