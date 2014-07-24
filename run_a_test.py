# -*- coding: cp1252 -*-
#
# this is a test class that run a python file in the converter package
# setting a minimum of sys path
#
#
import subprocess
import os, sys
import time
import zipfile
import traceback
import shutil
from base import ingester
from esaProducts import netCDF_reaper_product, eosip_product
from esaProducts import metadata
from esaProducts import definitions_EoSip
import imageUtil

#print "\nrun_a_test SYS_PATH:%s" % sys.path


debug=0


        
if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            print "will run file:%s" % sys.argv[1]
            #subprocess.Popen(sys.argv[1], shell=True)
            cmd=''
            script=sys.argv[1]
            aa=[]
            for i in range(len(sys.argv)-1):
                cmd="%s%s " % (cmd, sys.argv[i+1])
            for i in range(len(sys.argv)-2):
                aa.append(sys.argv[i+2])
            #print "command:'%s'" % cmd
            #print "aa:'%s'" % aa
            sys.argv=aa
            execfile(script)
            #subprocess.call(aa, shell=True)
            print "done"
            
            
        else:
            print "syntax: run_a_test.py path_to_python_file"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
