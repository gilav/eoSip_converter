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
    path='dummy_path'
    size=0
    origName=None
    folder=None
    type=None
    metadata=None
    TYPE_UNKNOWN=0
    TYPE_MPH=1
    TYPE_DIR=2
    TYPE_EOSIP=3

    def __init__(self, p=None):
        if self.debug!=0:
            print " init class Product, path=%s" % p
        self.path=p
        self.size=0
        self.type=self.TYPE_UNKNOWN
        # the product original name
        self.origName=os.path.split(self.path)[1]
        self.folder=os.path.split(self.path)[0]
        if self.debug!=0:
            print " folder=%s" % self.folder
            print " origName=%s" % self.origName
        self.debug=0
        self.myInit()

    @abstractmethod
    def myInit(self):
        pass

    def getize(self):
        self.size=os.stat(self.path).st_size
        return self.size

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

    def writeToPath(self, path=None):
        if self.debug!=0:
            print " will write product at path:%s" % path
        return None

    def parseFileName(self):
        if self.debug!=0:
            print " will parse filename"
        pass

    def getMetadataInfo(self):
        if self.debug!=0:
            print " will get metadata info"
        return None

    def extractMetadata(self):
        if self.debug!=0:
            print " will extract metadata"
        return None

    def setMetadata(self, m=None):
        if self.debug!=0:
            print " set metadata to:%s" % m
        self.metadata=m

    def buildTypeCode(self):
        return None

    def dumpMetadata(self):
        self.metadata.dump()
    

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=Product("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.read(1000)
    except Exception, err:
        log.exception('Error from throws():')

