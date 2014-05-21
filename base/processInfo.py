#
# classe used during the product procesing
# hold
# - the source and destination product
# - the tmpWorkig folder
# - the ingester used
#


class processInfo():

    def __init__(self):
        self.workFolder=None
        self.srcPath=None
        self.prodLog=''
        self.num=-1
        self.srcProduct=None
        self.destProduct=None
        self.eosipTmpFolder=None
        self.ingester=None
        print "init processInfo"

    def addLog(self, mess):
        try:
            self.prodLog="%s%s\n" % (self.prodLog, mess)
        except:
            print " ERROR: processInfo.addLog problem"
            pass

    
    def toString(self):
        res='\nworkFolder:%s\n' % self.workFolder
        res='%ssrcPath:%s\n' % (res, self.srcPath)
        res='%snum:%s\n' % (res, self.num)
        res='%ssrcProduct:%s\n' % (res, self.srcProduct)
        res='%sdestProduct:%s\n' % (res, self.destProduct)
        res='%seosipTmpFolder:%s\n' % (res, self.eosipTmpFolder)
        res='%singester:%s\n' % (res, self.ingester)
        return res
        
