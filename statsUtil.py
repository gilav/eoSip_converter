# -*- coding: cp1252 -*-
#
# 
#
#
import time,datetime
from esaProducts import formatUtils


debug=0


class StatsUtil():
    startTime=None
    totalSize=None
    totalTime=None
    total=None
    numDone=0
    endDate="not computed"
    
    #
    #
    #
    def __init__(self):
        print " init Stats class"
        self.startTime=None
        self.total=0
        self.totalTime=0
        self.totalSize=0
        self.numDone=0
        self.endDate="not computed"

    #
    #
    #
    def start(self, total):
        self.startTime=time.time()
        self.total=total

    #
    #
    #
    def oneDone(self, processingDuration=None, size=None):
        print " stats: add product[%d], size=%s; duration=%s" % (self.numDone, size, processingDuration)
        self.numDone=self.numDone+1
        if processingDuration!=None:
            self.totalTime=self.totalTime+processingDuration
        if size!=None:
            self.totalSize=self.totalSize+size
        self.calcEndDate()

    #
    #
    #
    def calcEndDate(self):
        avsize=self.totalSize/self.numDone
        avtime=self.totalTime/self.numDone
        if debug!=0:
            print " stats: calcEndDate: startTime=%s; avsize=%s; avtime=%s; totalSize=%s; totalTime=%s" % (self.startTime, avsize, avtime, self.totalSize, self.totalTime)
            print " stats: calcEndDate: avtime=%s; *=%s" % (avtime, (self.total-self.numDone))
            print " stats: calcEndDate: startTime to date:%s" % formatUtils.dateFromSec(self.startTime)
        finalTime = time.time() + (avtime *(self.total-self.numDone))
        self.endDate=formatUtils.dateFromSec(finalTime).replace("T", " ").replace("Z", "")

    
    #
    #
    #
    def getEndDate(self):
        return self.endDate
        
if __name__ == '__main__':
    pass
