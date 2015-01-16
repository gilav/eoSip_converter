import os, sys
import time
import traceback



class ProcessingUtils():

    #
    #
    #
    def __init__(self):
        print "create ProcessingUtils"

    def errorFileToList(self, path):
        if not os.path.exists(path):
            print "error:%s path does not exists" % path
        else:    
            print "errorFileToList on file:%s" % path
            outPath=path.replace(".log", ".list")
            print "will save it as:%s" % outPath
            fd=open(path, "r")
            fd1=open(outPath, "w")
            lines=fd.readlines()
            #print lines
            n=0
            print ""
            for line in lines:
                pos=line.find("|")
                print " product[%s] path:%s" % (n, line[0:pos])
                fd1.write("%s\n" % line[0:pos])
                n=n+1
            fd1.close()
            fd.close()
        
        
if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            pUtil = ProcessingUtils()
            pUtil.errorFileToList(sys.argv[1])
            
        else:
            print "syntax: python ProcessingUtils.py file"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
