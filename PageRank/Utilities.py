__author__ = 'Vardhman'

class CommandArguments(object):
    def __init__(self,qrel_file,query_mode ,rank_file):
        self.qrel_file = qrel_file
        self.query_mode = query_mode
        self.rank_file = rank_file
