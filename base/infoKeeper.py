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
    # add info pair: name=value
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
    # clear content
    #
    def clear(self):
            self.dictionnary={}


    #
    # return the key number
    #
    def size(self):
            return len(self.dictionnary.keys())


    #
    # return list of keys
    #
    def getKeys(self):
        keys=self.dictionnary.keys()
        keys.sort()
        return keys


    #
    # return list of values for a given key
    #
    def getKeyValues(self, key):
        if not self.dictionnary.has_key(key):
            raise Exception("unknown key:%s" % key)
        return self.dictionnary[key]

    #
    #
    #
    def toString(self):
        out=StringIO()
        print >>out, 'infoKeeper dump:'
        keys=self.dictionnary.keys()
        keys.sort()
        for info in keys:
                print >>out, "  info:'%s'" % info
                n=0
                values=self.dictionnary[info]
                values.sort()
                for value in values:
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
