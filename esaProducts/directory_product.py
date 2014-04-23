# -*- coding: cp1252 -*-
#
# this class is a base class for directory product
#
#
import os, sys
import re
import logging
from product import Product


class Directory_Product(Product):

    def __init__(self, path):
        Product.__init__(self, path)
        
    def myInit(self):
        print " init class Directory_Product"
        self.type=Product.TYPE_DIR
        

    def getContentFilename(self, path=None, regex=None):
        for file in os.listdir(path):
            print "  test file:%s" % file
        
        
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

