# -*- coding: cp1252 -*-
#
# this class is a base class for directory product
#
#
import os, sys
import re
import logging
import zipfile
from product import Product


class Directory_Product(Product):
    
    #
    #
    #
    def __init__(self, path):
        Product.__init__(self, path)
        print " init class Directory_Product"
        self.type=Product.TYPE_DIR
        self.contentList=[]
        
    #
    # write some source file in a zipStream
    #
    def writeInZip(self, zipStream=None, sourcePaths=None, sourceNames=None, compression=False):
        if isinstance(sourcePaths, list):
            n=0
            for oneSourcePath in sourcePaths:
                oneName=sourceNames[n]
                if compression==True:
                    zipStream.write(oneSourcePath, oneName, zipfile.ZIP_DEFLATED)
                else:
                    zipStream.write(oneSourcePath, oneName, zipfile.ZIP_STORED)
        else:
            if compression==True:
                zipStream.write(sourcePaths, sourceNames, zipfile.ZIP_DEFLATED)
            else:
                zipStream.write(sourcePaths, sourceNames, zipfile.ZIP_STORED) 

    def getContentFilename(self, path=None, regex=None):
        for file in os.listdir(path):
            print "  test file:%s" % file
        return os.listdir(path)
        
        
    def getMetadataInfo(self):
        data=self.read(4*1024)
        print " extract metadata from:%s" % data
        return None

    

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=Directory_Product("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.getMetadataInfo()
    except Exception, err:
        log.exception('Error from throws():')

