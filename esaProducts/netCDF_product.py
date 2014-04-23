# -*- coding: cp1252 -*-
#
# this class is a base class for directory product
#
#
import os, sys
import re
import logging
import traceback
from product import Product
netCDFloaded=False
try:
    from netCDF4 import Dataset
    netCDFloaded=True
except:
    print "ERROR: can not import netCDF4 package"





class netCDF_Product(Product):
    global netCDFloaded

    def __init__(self, path):
        global netCdfReady
        Product.__init__(self, path)
        print " init class netCDF_Product"
        self.netCdfReady=netCDFloaded
        self.type=Product.TYPE_NETCDF
        self.dataset=None

        
    #
    # return the dataset object
    #
    def getMetadataInfo(self):
        if self.netCdfReady:
            #if self.debug!=0:
            print " use netCDF4 package"
            if self.debug!=0:
                print " read dataset from path:%s" % self.path
            self.dataset=Dataset(self.path, 'r')
            if self.debug!=0:
                print "dataset:%s" % self.dataset
            return self.dataset
        else:
            if self.debug!=0:
                print " dont use netCDF4 package"
        return self.dataset
        
        

if __name__ == '__main__':
    print "start"
    try:
        p=netCDF_Product("C:/Users/glavaux/Shared/LITE/reaper/a.NC")
        p.getMetadataInfo()
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print "Error:%s  %s\n%s" %  (exc_type, exc_obj, traceback.format_exc())

