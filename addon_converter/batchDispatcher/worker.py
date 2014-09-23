#
# EoSip convertion using distributed worker
#
# the worker: it will convert a list of products
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
from math import sqrt
import random, time


try:
    import queue
except ImportError:
    import Queue as queue
import Pyro4


# we're using custom classes, so need to use pickle
Pyro4.config.SERIALIZER = 'pickle'

WORKERNAME = "Worker_%d@%s" % (os.getpid(), socket.gethostname())
numRun=0


#
# TODO: rn the converter...
#
def doJob(item):
    global numRun
    #s=int(random.random()*3)
    #print(" slepping %s sed" % s)
    #time.sleep(s)
    numRun=numRun+1
    return "[%s]: done job[%d]:%s" % (WORKERNAME, numRun, item.itemId)


#
# process a job
#
def process(item):
    print(" [%s]: processing itemId:%s" % (WORKERNAME,item.itemId))
    sys.stdout.flush()
    item.result = doJob(item)
    print(" ==> result: %s" % item.result)
    item.processedBy = WORKERNAME


#
# continuously pull the dispatcher for new job
#
def main():
    global numRun
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
    main()
