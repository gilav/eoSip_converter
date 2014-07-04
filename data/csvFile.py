#!/usr/bin/env python
#
# 
# Lavaux Gilles 2014
#
# This class is used to get values from CSV files
# used for Tropforest with the quality report excells 
#
#
import sys
import traceback
import csv


class csvData():
    reader=None
    key=None
    headers=None
    numLines=-1
    lut=None
    debug=0

    def __init__(self):
        print " init csvData"

    #
    # open a csv file
    #
    def openFile(self, path, key=None, name=None):
        fd=open(path, 'r')
        self.reader=csv.DictReader(fd, delimiter=',')
        n=0
        doLut=True
        for row in self.reader:
            if n==0:
                self.headers=row.keys()
                if self.debug!=0:
                    print "headers:%s" % self.headers
                if key!=None and name!=None:
                    try:
                        i1=self.headers.index(key)
                        i2=self.headers.index(name)
                        if self.debug!=0:
                            print "can create lut: i1=%d; i2=%d" % (i1, i2)
                        self.lut={}
                    except:
                        print "can not create lut: csv file has no column '%s' or '%s'" % (key, name)
                        doLut=False
                else:
                    doLut=False
                    
            if doLut:
                a=row[key]
                b=row[name]
                if self.debug!=0:
                    print " lut entry[%d]:%s==>%s" % (n, a, b)
                self.lut[a]=b
                    
            n=n+1
        self.numLines=n
        print "csv file %s opened, num lines:%s" % (path, self.numLines)
        if self.debug!=0:
            print "dir:%s" % dir(self.reader)
        if doLut==False:
            raise Exception("cvsFile '%s' error: has no column:'%s' or '%s' needed to build LUT" % (path, key, name))



    #
    # get a value
    #
    def getRowValue(self, k):
        if self.lut.has_key(k):
            return self.lut[k]
        else:
            return None
        
    #
    # get values
    #
    def getRowValues(self):
        return self.lut.values()

    #
    #
    #
    #def 

        
if __name__ == '__main__':
    try:
        csvd = csvData()
        #csvd.openFile("C:/Users/glavaux/Shared/LITE/testData/TropForest/status_AVNIR_qc_Final.csv", 'New_Filename', 'Orbit')
        #csvd.openFile("C:/Users/glavaux/Shared/LITE/Spot/MMMC_SPOT_export.csv", 'DATASET_ID', 'TRACK')
        csvd.openFile("C:/Users/glavaux/Shared/LITE/Spot/MMMC_SPOT_export.csv", 'DATASET_ID', 'PRODUCT_ID')
        #print "get N02-W062_KOM_20101110_PRO_0 Orbit:%s" % csvd.getRowValue('N00-W075_AVN_20090804_PRO_0')
        print "get N02-57172150608221305471J0_1A_DVD.ZIP PRODUCT_ID:%s" % csvd.getRowValue('57172150608221305471J0_1A_DVD.ZIP')
        print "get 40202630705261133411I0_1A_NETWORK.ZIP PRODUCT_ID:%s" % csvd.getRowValue('40202630705261133411I0_1A_NETWORK.ZIP')
        #print "get toto Orbit:%s" % csvd.getRowValue('toto')

        values = csvd.getRowValues()
        values.sort()
        typecode={}
        for item in values:
            pos=item.find('.')
            if pos > 0:
                typecode[item[pos+1:]]=item

        for item in typecode.keys():
            print item
            
        
        
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
