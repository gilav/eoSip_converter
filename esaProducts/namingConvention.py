# -*- coding: cp1252 -*-
#
# represent the EoSip naming convention
#

import os, sys
import logging
from product import Product
#from metadata import Metadata
import metadata
import formatUtils



class NamingConvention(Product):
    PATTERN='<SSS>_<CCCC>_<TTTTTTTTTT>_<instance ID>.<extension>'
    PATTERN_GENERIC='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<vvvv>'
    PATTERN_WRS_SCENE='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<oooooo>_<tttt>_<ffff>_<vvvv>'
    PATTERN_WRS_STRIPLINE='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<oooooo>_<tttt>_<vvvv>'
    usedPattern=None

    debug=0
    
    def __init__(self, p=PATTERN_GENERIC):
        if p[0]!='<':
            self.usedPattern=eval("NamingConvention.%s" % p)
        else:
            self.usedPattern=p

    def setDebug(self, d):
        self.debug=d

    def buildProductName(self, met=None, ext=None):
        if self.debug!=0:
            print " NamingConvention.buildProductName, pattern used:%s" % self.usedPattern
        toks = self.PATTERN.split('_')
        res=''
        for tok in toks:
            if self.debug!=0:
                print "doing token:%s" % tok
            if tok=='<SSS>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_PLATFORM), len(tok)-3, None, 1).upper()
                tmp1=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_PLATFORM_ID), len(tok)-4, None, 1)
                res="%s%s" % (tmp, tmp1)
                if self.debug!=0:
                    print "res is now:%s"% res
            elif tok=='<CCCC>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_FILECLASS), len(tok)-2)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "res1 is now:%s"% res
            elif tok=='<TTTTTTTTTT>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_TYPECODE), 10)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "res2 is now:%s"% res
            elif tok=='<instance ID>.<extension>':
                tmp=self.buildInstance(met)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "res3 is now:%s"% res
        if ext!=None:
            res="%s.%s" % (res, ext)
        return res


    def buildInstance(self, met=None):
        res=''
        for tok in self.usedPattern.split('_'):
            if self.debug!=0:
                print "doing instance token:%s" % tok
            if tok=='<yyyymmddThhmmss>':
                tmp=formatUtils.normaliseDate(met.getMetadataValue(metadata.METADATA_START_DATE), 8)
                tmp1=formatUtils.normaliseTime(met.getMetadataValue(metadata.METADATA_START_TIME), 6)
                res="%sT%s" % (tmp, tmp1)
                if self.debug!=0:
                    print "res4 is now:%s"% res
            if tok=='<YYYYMMDDTHHMMSS>':
                tmp=formatUtils.normaliseDate(met.getMetadataValue(metadata.METADATA_STOP_DATE), 8)
                tmp1=formatUtils.normaliseTime(met.getMetadataValue(metadata.METADATA_STOP_TIME), 6)
                res="%s_%sT%s" % (res, tmp, tmp1)
                if self.debug!=0:
                    print "res5 is now:%s"% res
            if tok=='<vvvv>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_VERSION), len(tok)-2)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resV is now:%s"% res
            if tok=='<oooooo>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_ORBIT), len(tok)-2, '0')
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resO is now:%s"% res
            if tok=='<tttt>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_TRACK), len(tok)-2)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resT is now:%s"% res
            if tok=='<ffff>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_FRAME), len(tok)-2)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resF is now:%s"% res
        return res


    def normaliseTime_NOT_USED(self, s=None, max=-1, pad='0'):
        if s != None:
            return s.replace(':', '')
        else:
            s=''
            while len(s)<max:
             s="%s%s" % (s, pad)
            return s
                
    def normaliseNumber_NOT_USED(self, s=None, max=-1, pad=' '):
        if self.debug==1:
            print "normaliseNumber:%s"% s
        if s==None:
            s="#"
            pad='#'
        if len(s) > max:
            return s[0:max]
        while len(s)<max:
            s="%s%s" % (s, pad)
        return s
        

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        n=NamingConvention()
        met=Metadata()
        met.setMetadataPair(met.METADATA_PLATFORM,"AL")
        met.setMetadataPair(met.METADATA_PLATFORM_ID,"1")
        met.setMetadataPair(met.METADATA_FILECLASS,"OPER")
        met.setMetadataPair(met.METADATA_START_DATE,"20140302")
        met.setMetadataPair(met.METADATA_START_TIME,"01:02:03")
        met.setMetadataPair(met.METADATA_STOP_DATE,"20150302")
        met.setMetadataPair(met.METADATA_STOP_TIME,"21:02:03")
        met.setMetadataPair(met.METADATA_FILECLASS,"OPER")
        met.setMetadataPair(met.METADATA_ORBIT,"1000")
        met.setMetadataPair(met.METADATA_TRACK,"273")
        met.setMetadataPair(met.METADATA_FRAME,"34")
        met.setMetadataPair(met.METADATA_VERSION,"00001")
        print n.buildProductName(met)
    except Exception, err:
        log.exception('Error from throws():')

