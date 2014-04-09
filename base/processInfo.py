

class processInfo():

    def __init__(self):
        self.workFolder=None
        self.srcPath=None
        self.prodLog=''
        self.num=-1
        self.srcProduct=None
        self.destProduct=None
        self.eosipTmpFolder=None
        print "init processInfo"

    def addLog(self, mess):
        self.prodLog="%s%s\n" % (self.prodLog, mess)

    
    def toString(self):
        res='workFolder:%s\n' % self.workFolder
        res='%ssrcPath:%s\n' % (res, self.srcPath)
        res='%snum:%s\n' % (res, self.num)
        res='%sproduct:%s\n' % (res, self.product)
        return res
        
