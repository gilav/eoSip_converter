# -*- coding: cp1252 -*-
#
# this class is a base class for directory product
#
# can represent a folder
# or a zip file
# or a bunch of various files/link
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
    def __init__(self, path, isAFolder=True):
        Product.__init__(self, path)
        print " init class Directory_Product"
        self.type=Product.TYPE_DIR

        # the content. path
        self.contentList=[]

        #the size of the contained files
        self.size=0



    #
    # add a file to the product content list
    #
    def addFile(self, path):
        self.contentList.append(path)

        if os.path.exists(path):
            self.size=self.size + os.stat(path).st_size

        
    #
    #
    #
    def getSize(self):
        return self.size
    
        
    #
    #
    #
    def getMetadataInfo(self):
        return None


        
    #
    # utility: write some source file in a zipStream
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
    

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=Directory_Product("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.getMetadataInfo()
    except Exception, err:
        log.exception('Error from throws():')

