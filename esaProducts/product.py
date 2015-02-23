# -*- coding: cp1252 -*-
#
# this class is a base class for Esa products
#
#
from abc import ABCMeta, abstractmethod
import os, sys
import logging


class Product:
    debug=0
    type=None
    TYPE_UNKNOWN=0
    TYPE_MPH=1
    TYPE_DIR=2
    TYPE_EOSIP=3
    TYPE_NETCDF=4

    #
    #
    #
    def __init__(self, p=None):
        if self.debug!=0:
            print " init class Product, path=%s" % p
        self.path=p
        self.metadata=None
        self.size=0
        self.type=self.TYPE_UNKNOWN
        self.contentList=[]
        if p==None:
            return
        # the product original name
        self.origName=os.path.split(self.path)[1]
        self.folder=os.path.split(self.path)[0]
        if self.debug!=0:
            print " folder=%s" % self.folder
            print " origName=%s" % self.origName

    #
    #
    #
    def getSize(self):
        self.size=os.stat(self.path).st_size
        return self.size

    #
    #
    #
    def read(self, size=0):
        if self.debug!=0:
            print " will read product"
        if not os.path.exists(self.path):
            raise  Exception("no product at path:%s" % self.path)
        fd = open(self.path, "r")
        data=fd.read(size)
        fd.close()
        if self.debug!=0:
            print " product readed"
        return data

    #
    #
    #
    def writeToPath(self, path=None):
        if self.debug!=0:
            print " will write product at path:%s" % path
        return None

    #
    #
    #
    def parseFileName(self):
        if self.debug!=0:
            print " will parse filename"
        pass

    #
    #
    #
    @abstractmethod
    def getMetadataInfo(self):
        if self.debug!=0:
            print " will get metadata info"
        return None
    
    #
    #
    #
    @abstractmethod
    def extractMetadata(self, processInfo):
        if self.debug!=0:
            print " will extract metadata"
        return None

    
    #
    # set product metadata
    #
    def setMetadata(self, m=None):
        if self.debug==0:
            print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ set metadata to:%s" % m
            print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ set metadata to values:%s" % m.toString()
            if self.metadata==None:
                print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current metadata :None"
            else:
                print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current metadata :%s" % self.metadata

        
        if self.metadata==None:
            self.metadata=m
        else:
            # add to existing one
            # dict name/values
            for key in m.getMetadataNames():
                print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ set metadata name:%s" % key
                self.metadata.setMetadataPair(key, m.getMetadataValue(key))
                print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@            values:%s" % m.getMetadataValue(key)
            # other info
                self.metadata.otherInfo = m.otherInfo
            # local attributes
                self.metadata.localAttributes = m.localAttributes
            # xml mapping
                

    #
    #
    #
    @abstractmethod
    def buildTypeCode(self):
        return None


    #
    # set debug flag
    #
    def setDebug(self, b):
        self.debug=b
    

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=Product("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.read(1000)
    except Exception, err:
        log.exception('Error from throws():')

