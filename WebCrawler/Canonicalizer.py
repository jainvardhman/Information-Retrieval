import urllib


__author__ = 'Vardhman'

from urllib.parse import urlsplit,urlparse,urlunparse,quote,unquote
import hashlib
import re

# "(:)[\d]+"
REGEX_NETLOC_HTTP  = "(:80)"
REGEX_NETLOC_HTTPS = "(:443)"
REGEX_PATH = "((^[/](index|default|home)$)|(^[/](index|default|home)[\.]{1}[a-z]+)$)"

# unquote is used to convert all the octets to the correct characters
url = "http://www.google.com/new/mypage.html?a=c#mdl"
      #"%7Eabout/?page_id=758"
#--url_unq  = unquote(url)
# gets the domain name of the url
#--base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url_unq))

# the hashing done below should be used in order to store ids in the elastic search
# or for any other purpose of url matching so that it is consistent and no
# string matching anomalies are generated

# does sha224 encoding- has a larger size
#--print(hashlib.sha224(base_url.encode('utf-8')).hexdigest())#digest_size)

# does md5 encoding- has a smaller size
#--m = hashlib.md5()
#--m.update(base_url.encode('utf-8'))
#--print(m.digest())#digest_size)


# canonicalization - has to be done before hashing, not needed in case of extracting domain name
# only needed when we actually store in frontier and visit these links
# uses the url parse library, which splits the url into various sections
# these sections can now be individually treated for canonicalization and the
# url should be reformed

#--parseResult = urlparse(url_unq)
#parseResult.netloc = re.sub("(:)[\d]+","",parseResult.netloc)
#--print(base_url)
#--print(parseResult)
#--print(type(parseResult))

def getCanonicalizedUrl(parseResult,currentdomain):
    currentdomainParseResult = urlparse(currentdomain)
    scheme = str.lower(coalesc(parseResult.scheme,currentdomainParseResult.scheme))
    if scheme == "https":
        netloc = str.lower(re.sub(REGEX_NETLOC_HTTPS,"",coalesc(parseResult.netloc,currentdomainParseResult.netloc)))
    else:
        netloc = str.lower(re.sub(REGEX_NETLOC_HTTP,"",coalesc(parseResult.netloc,currentdomainParseResult.netloc)))
    path = canonicalizePath(parseResult,currentdomainParseResult)# re.sub(REGEX_PATH,"",coalesc(unquote(parseResult.path),currentdomainParseResult.path)).lstrip(".").replace("//","/")
    params= ""
    query= ""
    fragment = ""
    return (urlunparse(urllib.parse.ParseResult(scheme,netloc,path,params,query,fragment)))


def canonicalizePath(parseResult,currentdomainParseResult):
    path = re.sub(REGEX_PATH,"",coalesc(unquote(parseResult.path),currentdomainParseResult.path)).lstrip(".").replace("//","/")
    path = re.sub("([\.]+)(\/)","",path)
    return path

def coalesc(first,second):
    if first == "":
        return second
    else:
        return first

def decode_octets(stri):
    unq_url = unquote(stri)
    return  unq_url

def canonicalizeMain(url,currentUrl,encodingType):
    urlun = url #decode_octets(url)
    return getCanonicalizedUrl(urlparse(urlun),currentUrl)


