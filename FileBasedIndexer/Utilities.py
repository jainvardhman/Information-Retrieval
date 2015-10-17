class DocumentBlock(object):
    def __init__(self, docId, posList):
        self.docId = docId
        self.posList = posList

class OffsetMap(object):
    def __init__(self,startPos,bytesToRead):
        self.startPos = startPos
        self.bytesToRead = bytesToRead
