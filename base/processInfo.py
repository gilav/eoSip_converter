#
# classe used during the product procesing
# hold
# - the source and destination product
# - the tmpWorkig folder
# - the ingester used
#
from cStringIO import StringIO
import os,sys
import time
from datetime import datetime
import traceback


#
#
#
DEFAULT_DATE_PATTERN="%Y-%m-%d %H:%M:%S"
def dateNow(pattern=DEFAULT_DATE_PATTERN):
        d=datetime.fromtimestamp(time.time())
        return d.strftime(pattern)

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
        self.error=''
        self.test_dont_extract=False
        self.test_dont_write=False
        self.test_dont_do_browse=False
        self.infoKeeper=None
        self.ingester=None
        print "init processInfo"


    def addInfo(self, n, v):
            if self.infoKeeper!=None:
                    self.infoKeeper.addInfo(n,v)
            else:
                    raise Exception("no infoKeeper")

    def addLog(self, mess):
        try:
            #now=dateNow()
            self.prodLog="%s%s: %s\n" % (self.prodLog, dateNow() , mess)
        except:
            print " ERROR: processInfo.addLog problem"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.error="%s%s%s\n" % (self.error, exc_type, exc_obj)
            pass

    
    def toString(self):
        out=StringIO()
        print >>out, '\nworkFolder:%s' % self.workFolder
        print >>out, 'srcPath:%s' % (self.srcPath)
        print >>out, 'num:%s' % (self.num)
        print >>out, 'srcProduct:%s' % (self.srcProduct)
        print >>out, 'destProduct:%s' % (self.destProduct)
        print >>out, 'ingester:%s' % (self.ingester)
        print >>out, 'eosipTmpFolder:%s' % (self.eosipTmpFolder)
        
        print >>out, '!! test_dont_extract:%s' % (self.test_dont_extract)
        print >>out, '!! test_dont_write:%s' % (self.test_dont_write)
        print >>out, '!! test_dont_do_browse:%s' % (self.test_dont_do_browse)
        
        print >>out, 'Error:%s' % (self.error)
        print >>out, 'LOG:\n%s' % (self.prodLog)
        return out.getvalue()
        

if __name__ == '__main__':
        print "start"
        pinfo = processInfo()
        #pinfo.addInfo("aa", "bbbb")
        pinfo.addLog("aa")
        print "pinfo:%s" % pinfo.toString()


        
