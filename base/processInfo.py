#
# classe used during the product procesing
# hold
# - the source and destination product
# - the tmpWorkig folder
# - the ingester used
#
from cStringIO import StringIO

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
        out=StringIO()
        print >>out, '\nworkFolder:%s\n' % self.workFolder
        print >>out, 'srcPath:%s\n' % (self.srcPath)
        print >>out, 'num:%s\n' % (self.num)
        print >>out, 'srcProduct:%s\n' % (self.srcProduct)
        print >>out, 'destProduct:%s\n' % (self.destProduct)
        print >>out, 'eosipTmpFolder:%s\n' % (self.eosipTmpFolder)
        print >>out, 'ingester:%s\n' % (self.ingester)
        return out.getvalue()
        
