# -*- coding: cp1252 -*-
#
# this is an helper for EoSip product
#
#
import os, sys
import re
import logging
import zipfile
from product import Product


class Eosip_product_helper():
    
    #
    #
    #
    def __init__(self, sipProduct):
        print " init class Eosip_product_helper"
        self.eoSipProduct=sipProduct


    #
    #
    #
    def getFileContent(self, path):
        if not os.path.exists(path):
            raise Exception("file does not exists:%s" % path)
        fd=open(path, 'r')
        data=fd.read()
        fd.close()
        return data

    #
    # return an item content of a zipFile item
    #
    # param path: path of zip file
    # param entry: name of the entry we want 
    #
    def getZipFileItem(self, path, entry):
            # get MD file in zip
            fh = open(path, 'rb')
            z = zipfile.ZipFile(fh)
            data=z.read(entry)
            z.close()
            fh.close()
            return data

    #
    # test if an zip item is compressed 
    #
    # param path: path of zip file
    # param entry: name of the entry we want 
    #
    def isZipFileItemCompressed(self, path, entry):
            # get MD file in zip
            fh = open(path, 'rb')
            z = zipfile.ZipFile(fh)
            zipInfo = z.getinfo(entry)
            z.close()
            fh.close()
            print " ## zip entry %s. Size:%s; compressed size:%s" % (entry, zipInfo.file_size, zipInfo.compress_size)
            return zipInfo.file_size != zipInfo.compress_size

            
    #
    # return the path and content of MD report
    #
    def getMdPart(self):
        if self.eoSipProduct.created:
            # get MD file in work folder
            return self.eoSipProduct.reportFullPath, self.getFileContent(self.eoSipProduct.reportFullPath)
        else:
            # get MD file in zip
            return self.eoSipProduct.reportFullPath, self.getZipFileItem(self.eoSipProduct.path, self.eoSipProduct.reportFullPath)

    #
    #
    #
    def getQrPart(self):
        if self.eoSipProduct.created:
            # get QR file in work folder
            return self.eoSipProduct.qualityReportFullPath, self.getFileContent(self.eoSipProduct.qualityReportFullPath)
        else:
            # get QR file in zip
            return self.eoSipProduct.qualityReportFullPath, self.getZipFileItem(self.eoSipProduct.path, self.eoSipProduct.qualityReportFullPath)

    #
    #
    #
    def getSiPart(self):
        if self.eoSipProduct.created:
            # get SI file in work folder
            return self.eoSipProduct.sipFullPath, self.getFileContent(self.eoSipProduct.sipFullPath)
        else:
            # get SI file in zip
            return self.eoSipProduct.sipFullPath, self.getZipFileItem(self.eoSipProduct.path, self.eoSipProduct.sipFullPath)
        
    #
    #
    #
    def getBrowsePart(self, browseIndex=0):
        if len(self.sourceBrowsesPath)==0:
            raise Exception("no browse")
            
        if self.eoSipProduct.created:
            # get browse[n] file in work folder
            return self.eoSipProduct.sipFullPath, self.getFileContent(self.eoSipProduct.sipFullPath)
        else:
            # get browse[n] file in zip
            return self.eoSipProduct.sipFullPath, self.getZipFileItem(self.eoSipProduct.path, self.eoSipProduct.sipFullPath)
    #
    #
    #
    def getEoProductPart(self):
        pass


    #
    #
    #
    def getTypologyFromMdContent(self, data):
        pos = data.find(':EarthObservation')
        if pos>0:
            return data[pos-3:pos]
        else:
            if len(data) >50:
                tmp=data[0:50]
            else:
                tmp=data
            raise Exception("can not extract typology from:%s..." % tmp)
        
        
        

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        helper=Eosip_product_helper()
    except Exception, err:
        log.exception('Error from throws():')

