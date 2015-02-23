# -*- coding: cp1252 -*-
#
# represent the EoSip naming convention
#

import os, sys
import logging
from product import Product
import metadata
import formatUtils
from namingConvention import NamingConvention



class NamingConvention_Aeolus(NamingConvention):
    
    #
    # Aeolus pattern
    EOLUS_PATTERN='<AE>_<CCCC>_<TTTTTTTTTT>_<instance ID>.<extension>'
    EOLUS_PATTERN_INSTANCE_GENERIC_DTOV='<yyyymmddThhmmsszzz>_<uuuuuuuuu>_<oooooo>_<vvvv>'
    EOLUS_PATTERN_INSTANCE_GENERIC_DDV='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<vvvv>'

    #
    AEOLUS_POSSIBLE_PATTERN=[EOLUS_PATTERN_INSTANCE_GENERIC_DTOV, EOLUS_PATTERN_INSTANCE_GENERIC_DDV]
    
    #
    usedBase=None
    usedPattern=None

    debug=0

    #
    #
    #
    def __init__(self, p=EOLUS_PATTERN_INSTANCE_GENERIC_DTOV, fromSuper=False):
        NamingConvention.__init__(self, p, True)
        #super(NamingConvention_Aeolus, self).__init__(p)
        #global usedBase

        # the possible pattern used
        for item in self.AEOLUS_POSSIBLE_PATTERN:
            try:
                self.possible_pattern.index(item)
            except:
                self.possible_pattern.append(item)

        if self.debug!=0:
            print " #### NamingConvention_Aeolus p=%s" % p
            
        if p[0]!='<':
            if self.debug!=0:
                print "NamingConvention init case 0: pattern=%s" % p
            self.usedPattern=eval("NamingConvention_Aeolus.%s" % p)
            self.usedBase=NamingConvention_Aeolus.EOLUS_PATTERN
            print " NamingConvention_Aeolus usedPattern=%s" % self.usedPattern
        else:
            self.usedPattern=p
            self.usedBase=NamingConvention_Aeolus.EOLUS_PATTERN
            print " NamingConvention_Aeolus init case 1: usedPattern=%s" % self.usedPattern

    #
    #
    #
    def buildProductName(self, met=None, ext=None):
        if self.debug!=0:
            print " NamingConvention_Aeolus.buildProductName, pattern used:%s, ext:%s" % (self.usedPattern, ext)
        toks = self.EOLUS_PATTERN.split('_')
        res=''
        for tok in toks:
            if self.debug!=0:
                print "doing token:%s" % tok
            if tok=='<AE>':
                res=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_PLATFORM), len(tok)-2, None, 1).upper()
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


    #
    #
    #
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
            if tok=='<yyyymmddThhmmsszzz>':
                tmp=formatUtils.normaliseDate(met.getMetadataValue(metadata.METADATA_START_DATE), 8)
                tmp1=formatUtils.normaliseTime(met.getMetadataValue(metadata.METADATA_START_TIME), 6)
                tmp2=formatUtils.normaliseTime(met.getMetadataValue(metadata.METADATA_START_TIME_MSEC), 3)
                res="%s_%sT%s%s" % (res, tmp, tmp1, tmp2)
                if self.debug!=0:
                    print "res5 is now:%s"% res
            if tok=='<uuuuuuuuu>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_DURATION), 8)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "res5 is now:%s"% res
            if tok=='<YYYYMMDDTHHMMSS>':
                tmp=formatUtils.normaliseDate(met.getMetadataValue(metadata.METADATA_STOP_DATE), 8)
                tmp1=formatUtils.normaliseTime(met.getMetadataValue(metadata.METADATA_STOP_TIME), 6)
                res="%s_%sT%s" % (res, tmp, tmp1)
                if self.debug!=0:
                    print "res5 is now:%s"% res
            if tok=='<vvvv>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_SIP_VERSION), len(tok)-2)
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resV is now:%s"% res
            if tok=='<oooooo>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_ORBIT), len(tok)-2, '0')
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resO is now:%s"% res
            if tok=='<tttt>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_TRACK), len(tok)-2, '0')
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resT is now:%s"% res
            if tok=='<ffff>':
                tmp=formatUtils.normaliseNumber(met.getMetadataValue(metadata.METADATA_FRAME), len(tok)-2, '0')
                res="%s_%s" % (res, tmp)
                if self.debug!=0:
                    print "resF is now:%s"% res
        return res


        

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    filename='AE_TEST_ALD_U_N_2B_20110409T064002_20110409T081238_0001.DBL'
    try:
        n=NamingConvention_Aeolus()
        print "namingConvention dump:%s" % n.toString()

        res = n.guessPatternUsed(filename, n.possible_pattern )
        if len(res)==1:
            n.usePatternvalue(res[0])
        else:
            print "can not find instance pattern..."


        ptype=n.getFilenameElement(filename, NamingConvention_Aeolus.EOLUS_PATTERN, 'TTTTTTTTTT')
        print "productType=%s" % ptype
        
        sys.exit(0)
        
        met=metadata.Metadata()
        met.setMetadataPair(metadata.METADATA_PLATFORM,"AL")
        met.setMetadataPair(metadata.METADATA_PLATFORM_ID,"1")
        met.setMetadataPair(metadata.METADATA_FILECLASS,"OPER")
        met.setMetadataPair(metadata.METADATA_START_DATE,"20140302")
        met.setMetadataPair(metadata.METADATA_START_TIME,"01:02:03")
        met.setMetadataPair(metadata.METADATA_STOP_DATE,"20150302")
        met.setMetadataPair(metadata.METADATA_STOP_TIME,"21:02:03")
        met.setMetadataPair(metadata.METADATA_FILECLASS,"OPER")
        met.setMetadataPair(metadata.METADATA_ORBIT,"1000")
        met.setMetadataPair(metadata.METADATA_TRACK,"273")
        met.setMetadataPair(metadata.METADATA_FRAME,"34")
        met.setMetadataPair(metadata.METADATA_SIP_VERSION,"00001")
        met.setMetadataPair(metadata.METADATA_TYPECODE,"HRV__X__1A")
        print n.buildProductName(met)
    except Exception, err:
        log.exception('Error from throws():')

