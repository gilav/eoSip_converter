# -*- coding: cp1252 -*-
#
# this class represent a folder containing several Eo products
# based on the Folder_With_Products
# 
#
#
#
import os, sys
import re
import logging
import zipfile
from product import Product
import metadata
from netCDF_reaper_product import NetCDF_Reaper_Product
from folder_with_products import Folder_With_Products
import formatUtils


class Reaper_Cycle(Folder_With_Products):
    
    #
    #
    #
    def __init__(self, path):
        Folder_With_Products.__init__(self, path, False)
        self.start=None
        self.stop=None
        print " init class Reaper_Product_Cycle"

    
        
    #
    # return common metadata:
    #  - min start date, max stop date
    #
    def getMetadataInfo(self):
        return None


    #
    #
    #
    def extractMetadata(self, met=None):
        if met==None:
            raise Exception("metadate is None")
        # extract metadata from each product
        for path in self.contentList:
            print " extract metadata from:%s" % path
            p=NetCDF_Reaper_Product(path)
            p.getMetadataInfo()
            pMet=metadata.Metadata()
            p.extractMetadata(pMet)
            p.refineMetadata()

            startDate = p.metadata.getMetadataValue(metadata.METADATA_START_DATE)
            startTime = p.metadata.getMetadataValue(metadata.METADATA_START_TIME)

            stopDate = p.metadata.getMetadataValue(metadata.METADATA_STOP_DATE)
            stopTime = p.metadata.getMetadataValue(metadata.METADATA_STOP_TIME)

            print "  start date:%s" % startDate
            print "  start time:%s" % startTime
            print "  stop date:%s" % stopDate
            print "  stop time:%s" % stopTime

            t1 = formatUtils.timeFromDatePatterm("%sT%sZ" % (startDate, startTime))
            t2 = formatUtils.timeFromDatePatterm("%sT%sZ" % (stopDate, stopTime))
            
            if self.start==None:
                self.start=t1
            else:
                if t1<self.start:
                    self.start=t1
            
            if self.stop==None:
                self.stop=t2
            else:
                if t2>self.stop:
                    self.stop=t2
        #
        met.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, self.getSize())
        self.metadata=met
        return 1

        
    #
    # refine the metada
    #
    def refineMetadata(self):
        #print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%% TUTU"
        self.metadata.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, self.getSize())
        tmp = formatUtils.dateStringFromTime(self.start).replace('Z','')
        print "  refine start date:%s" % tmp
        self.metadata.setMetadataPair(metadata.METADATA_START_DATE, tmp.split('T')[0])
        self.metadata.setMetadataPair(metadata.METADATA_START_TIME, tmp.split('T')[1])

        tmp = formatUtils.dateStringFromTime(self.stop).replace('Z','')
        print "  refine stop date:%s" % tmp
        self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, tmp.split('T')[0])
        self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, tmp.split('T')[1])
        



        

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=Reaper_Cycle("C:/Users/glavaux/Shared/LITE/testData/Reaper/SGDR")
        p.addFile('C:/Users/glavaux/Shared/LITE/testData/Reaper/GDR/E1_REAP_ERS_ALT_2__19910803T224655_19910804T002529_RP01.NC')
        p.addFile('C:/Users/glavaux/Shared/LITE/testData/Reaper/GDR/E2_TEST_ERS_ALT_2__20010212T060425_20010212T080124_COM5.NC')

        print "product full size:%s" % p.getSize()
        met = p.getMetadataInfo()
        print "metadata:%s" % met
        
    except Exception, err:
        log.exception('Error from throws():')

