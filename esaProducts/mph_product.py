# -*- coding: cp1252 -*-
import os, sys
import logging
from Product import Product


class MphProduct(Product):
    
    def __init__(self, p=None):
        Product.__init__(self, path)
        print " init class MphProduct, path=%s" % p
        self.path=p
        self.type=Product.TYPE_MPH

    def getMetadataInfo(self):
        data=self.read(4*1024)
        print " extract metadata from:%s" % data
        return None
    

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=MphProduct("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.getMetadataInfo()
    except Exception, err:
        log.exception('Error from throws():')

