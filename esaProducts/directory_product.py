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
    
    def __init_disabled__(self, p=None):
        print " init class Directory_Product, path=%s" % p
        self.path=p
        self.type=Product.TYPE_DIR

    def myInit(self):
        #if self.debug!=0:
        print " init class Dimap_Product"
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

