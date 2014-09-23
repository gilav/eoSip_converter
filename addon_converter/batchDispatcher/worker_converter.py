#
# EoSip convertion using distributed worker
#
# the converter worker: it will convert a list of products
# at startup it instanciate the converter
#  
#
#
# For Esa/lite dissemination project
#
# Serco 02014
# Lavaux Gilles 
#
# base on Pyro4 examples
#
# 21/09/2014: V: 0.1
#
#
#
from __future__ import print_function
import os
import socket
import sys
import traceback
from math import sqrt
import random, time


try:
    import queue
except ImportError:
    import Queue as queue
import Pyro4


# we're using custom classes, so need to use pickle
Pyro4.config.SERIALIZER = 'pickle'

#
workerId=0
converterName = None
converterPackage = None
WORKERNAME = "Worker_undefinedConverter%d@%s" % (os.getpid(), socket.gethostname())

#
numRun=0
debug=0

converterInstance = None


#
# TODO: rn the converter...
#
def doJob(item):
    global numRun, converterInstance, workerId
    exitCode=-9
    try:
        numRun=numRun+1
        converterInstance.processSingleProduct(item.products, numRun)
        exitCode=0
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exitCode=0
        item.error="Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
        
    return "[%s]: done job[%d]:%s" % (WORKERNAME, numRun, item.itemId)


#
# process a job
#
def process(item):
    print("\n [%s]: processing itemId:%s" % (WORKERNAME, item.itemId))
    print(" [%s]: product:%s" % (WORKERNAME, item.products))
    sys.stdout.flush()
    item.result = doJob(item)
    print(" ==> result: %s\n" % item.result)
    item.processedBy = WORKERNAME


#
# continuously pull the dispatcher for new job
#
# converterPackagePath as to be like: '...fullPath.../ingester_tropforest.py'
# 
# 
def main(converterPackagePath, converterConfigFile, index):
    global numRun, WORKERNAME, converterName, converterPackage, converterInstance, workerId
    workerId=index
    # extract the converter package name; ...fullPath.../ingester_tropforest.py  ==> ingester_tropforest.py
    # also the name (without .py)
    tmp = converterPackagePath.replace('\\','/')
    pos=tmp.rfind('/')
    if pos==-1:
        pos=0
        pos2=tmp.find('.')
    else:
        pos=pos+1
        pos2=tmp.find('.', pos)
    converterPackage=tmp[pos]
    converterName=tmp[pos:pos2]
    WORKERNAME = "Worker__converter_%s__%d@%s" % (converterName, os.getpid(), socket.gethostname())
    print(" I am worker:%s" % WORKERNAME)

    # add converter path to python path
    parentdir = os.path.dirname(converterPackagePath)
    if debug != 0:
        print("parentdir:%s" % parentdir)
    sys.path.insert(0, parentdir)
    if debug != 0:
        print("sys.path:%s" % sys.path)


    # create converter
    module = __import__(converterName)
    print(" converter package imported")
    class_ = getattr(module, converterName)
    print(" converter module imported")
    converterInstance = class_()
    print(" got converter instance")
    print(" converter instance:%s" % converterInstance)

    # start sonverter
    args=[]
    args.append("-c")
    args.append(converterConfigFile)
    args.append("-d")
    args.append("True")
    args.append("-i")
    args.append(index)
    converterInstance.starts(args)
    
    dispatcher = Pyro4.core.Proxy("PYRONAME:eosip.converter.dispatcher")
    print("This is worker %s" % WORKERNAME)
    print(" getting job from dispatcher.")
    while True:
        try:
            item = dispatcher.getWork()
        except queue.Empty:
            print(" [%s]: no job available yet, job done:%d" % (WORKERNAME, numRun))
        else:
            process(item)
            dispatcher.putResult(item)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 3:
            print("worker for converter:%s\n" % sys.argv[1])
            converterPath=sys.argv[1]
            converterConfigPath=sys.argv[2]
            index=sys.argv[3]
            main(converterPath, converterConfigPath, index)
            
        else:
            print("syntax: worker_converter.py path_to_converter.py path_to_converter_configuration workerIndex\n")
            print("  (where converter_path.py is the full path of the eosip_converter_package that will be used)\n")
            
    except:
        print(" init error:\n")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

                    
