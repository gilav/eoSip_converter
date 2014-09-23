#
# EoSip convertion using distributed worker
#
# the client: it will put a list of convertion batch to the dispatcher
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
from __future__ import with_statement
import sys

try:
    import queue
except ImportError:
    import Queue as queue
import random
import Pyro4
from workitem import Workitem

# we're using custom classes, so need to use pickle
Pyro4.config.SERIALIZER = 'pickle'

NUMBER_OF_ITEMS = -1

#
#
#
def main(argv):
    print("This client will create a list of batch to be executed by the distributed workers\n")
    print("The more workers you will start (on different cpus/cores/machines),")
    print("the faster you will get the complete list of results!\n")

    # first parameter is the path of a file containg list of product to process
    if len(sys.argv) >=2:
        fileList=sys.argv[1]
        print("using products list from file:%s" % fileList)
        fd=open(fileList, "r")
        lines=fd.readlines()
        fd.close()
        productList=[]
        n=0
        for line in lines:
            if line[0]!="#":
                path=line.replace("\\","/").replace('\n','')
                productList.append(path)
                n=n+1
        print("number of products:%d" % n)
    else:
        raise Exception("Syntax: python client.py productListFile [expectedNumberOfWorker]")

    # second parameter
    numWorker=1
    if len(sys.argv) >=3:
        numWorker=sys.argv[2]
        numWorker=int(numWorker)

    print("Expected number of workers:%d" % numWorker)

    
    
    with Pyro4.core.Proxy("PYRONAME:eosip.converter.dispatcher") as dispatcher:
        placework(dispatcher, productList)
        numbers = collectresults(dispatcher)
    printresults(numbers)


#
#
#
def placework(dispatcher, productList):
    global NUMBER_OF_ITEMS
    print("placing work items into dispatcher queue.")
    # calculate number of batch to do
    
    
    i=0
    for item in productList:
        workItem = Workitem(i + 1, "converterPath", "converterConfig", item, "batch")
        dispatcher.putWork(workItem)
        i=i+1
    NUMBER_OF_ITEMS=i


#
#
#
def collectresults(dispatcher):
    global NUMBER_OF_ITEMS
    print("getting results from dispatcher queue, number to retrieve:%d" % NUMBER_OF_ITEMS)
    numbers = {}
    while len(numbers) < NUMBER_OF_ITEMS:
        try:
            item = dispatcher.getResult()
            print("Got result: %s (from %s):%s" % (item.itemId, item.processedBy, item.result))
            numbers[item.itemId] = item.result
        except queue.Empty:
            print("Not all results available yet (got %d out of %d). Work queue size: %d" %
                  (len(numbers), NUMBER_OF_ITEMS, dispatcher.workQueueSize()))

    if dispatcher.resultQueueSize() > 0:
        print("there's still stuff in the dispatcher result queue, that is odd...")
    return numbers


def printresults(numbers):
    print("\nResults:")
    for (number, result) in numbers.items():
        print("%d --> %s" % (number, result))


if __name__ == "__main__":
    main(sys.argv)
