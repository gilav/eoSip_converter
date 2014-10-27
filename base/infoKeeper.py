#
# classe used to keep conversion information, for examplelist of typecode encountered
#
from cStringIO import StringIO
import os,sys
import time
import traceback


#
#
#
class infoKeeper():

    #
    #
    #
    def __init__(self):
        print "init infoKeeper"
        # data will be stored in a dictionnary. key=info, values is a list
        self.dictionnary={}


    #
    #
    #
    def addInfo(self, info, value):
        # info already there?
        valueList=None
        if self.dictionnary.has_key(info):
                valueList = self.dictionnary[info]
        else:
                # create new list
                valueList=[]
                self.dictionnary[info]=valueList
        # add if not already in list:
        try:
                valueList.index(value)
        except:
                #print " Error"
                #exc_type, exc_obj, exc_tb = sys.exc_info()
                #traceback.print_exc(file=sys.stdout)
                valueList.append(value)

    #
    #
    #
    def clear(self):
            self.dictionnary={}


    #
    #
    #
    def size(self):
            return len(self.dictionnary.keys())

    #
    #
    #
    def toString(self):
        out=StringIO()
        print >>out, 'infoKeeper dump:'
        for info in self.dictionnary.keys():
                print >>out, "  info:'%s'" % info
                n=0
                for value in self.dictionnary[info]:
                        print >>out, "    value[%d]:'%s'" % (n,value)
                        n=n+1
                
                
        return out.getvalue()
        


if __name__ == '__main__':
    try:
        keeper=infoKeeper()
        keeper.addInfo('typeCode', 'a')
        keeper.addInfo('typeCode', 'b')
        keeper.addInfo('typeCode', 'c')
        keeper.addInfo('sensor', 'sa')

        print "%s" % keeper.toString()

        
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
