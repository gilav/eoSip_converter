# -*- coding: cp1252 -*-
#
# represent the EoSip naming convention
#

import os, sys
import logging
from product import Product
import metadata
import formatUtils
from cStringIO import StringIO



class NamingConvention(Product):
    
    #
    # following used at start in NGEO branch
    PATTERN='<SSS>_<CCCC>_<TTTTTTTTTT>_<instance ID>.<extension>'
    PATTERN_INSTANCE_GENERIC_DDV='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<vvvv>'
    PATTERN_INSTANCE_WRS_SCENE_DDOTFV='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<oooooo>_<tttt>_<ffff>_<vvvv>'
    PATTERN_INSTANCE_WRS_STRIPLINE_DDOTV='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<oooooo>_<tttt>_<vvvv>'
    #
    # following used in OGC branch:
    PATTERN_INSTANCE_OGC_DDOTF='<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<oooooo>_<tttt>_<ffff>'
    #
    #
    POSSIBLE_PATTERN=[PATTERN_INSTANCE_GENERIC_DDV, PATTERN_INSTANCE_WRS_SCENE_DDOTFV, PATTERN_INSTANCE_WRS_STRIPLINE_DDOTV, PATTERN_INSTANCE_OGC_DDOTF]
    
    #
    #
    usedBase=None
    usedPattern=None




    debug=0

    #
    # init
    # build list of possible instance pattern than can be used
    #
    def __init__(self, p=PATTERN_INSTANCE_GENERIC_DDV, fromSuper=False):
        #
        self.possible_pattern=[]

        # the possible pattern used
        for item in self.POSSIBLE_PATTERN:
            self.possible_pattern.append(item)

        if self.debug!=0:
            print "#### NamingConvention p=%s\n#### possible length:%s\n#### possible=%s" % (p, len(self.possible_pattern), self.possible_pattern)
            
        self.usedBase=NamingConvention.PATTERN
        if p[0]!='<':
            if self.debug!=0:
                print " NamingConvention init case 0: pattern=%s" % p
            try:
                self.usedPattern=eval("NamingConvention.%s" % p)
            except:
                if fromSuper==True:
                    pass
                else:
                    raise Exception("pattern not found:%s" % p)
            #if self.debug!=0:
            print " NamingConvention usedPattern=%s" % self.usedPattern
        else:
            #
            self.usedPattern=p
            #if self.debug!=0:
            print " NamingConvention init case 1: usedPattern=%s" % self.usedPattern

    #
    # use a instance pattern, provide the string value like '<yyyymmddThhmmss>_<YYYYMMDDTHHMMSS>_<vvvv>'
    #
    def usePatternvalue(self, value):
        res=[]
        for item in self.possible_pattern:
            if value==item:
                res.append(item)
        if len(res)==1:
            return res[0]
        elif len(res)==0:
            raise Exception("can not find instance pattern with value:%s" % value)
        elif len(res)>1:
            raise Exception("several instance pattern match:%s" % res)

    #
    #
    #
    def setDebug(self, d):
        self.debug=d

    #
    # build the product name based on the metadata values
    #
    def buildProductName(self, met=None, ext=None):
        if self.debug!=0:
            print " NamingConvention.buildProductName, pattern used:%s, ext:%s" % (self.usedPattern, ext)
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


    #
    # return the length of the fileName. not including the extension
    #
    def getFilenameLength(self):
        return self.usedPattern.replace('<','').replace('>','')


    #
    # test if file has the correct length. extension should not be given
    #
    def isFileLengthOk(self, name):
        n=self.getFilenameLength()
        if len(name)==n:
            print "filename:%s has corect length:%d" % (name, len(name))
            return True
        else:
            print "filename:%s has incorect length:%d vs %s" % (name, len(name),n)
            return False

    
    #
    # get the filename length, as the used base and pattern define it
    #
    def getFilenameLength(self):
        base=len(self.usedBase.replace('<instance ID>.<extension>','').replace('<','').replace('>',''))
        instance=len(self.usedPattern.replace('<','').replace('>',''))
        return base + instance


    #
    # try to identify the (instance) pattern used
    #
    def guessPatternUsed(self, filename, possiblePattern):
        # cut out the base
        print " guessPatternUsed of:%s" % filename
        if self.debug!=0:
            print " self.usedBase:%s" % self.usedBase
        strippedBase=self.usedBase.replace('<instance ID>.<extension>','').replace('<','').replace('>','')
        if self.debug!=0:
            print " strippedBase:%s" % strippedBase
        tmp = filename[len(strippedBase):]
        print " instance part:%s" % tmp
        # look how many _ we have
        numSepFilename=tmp.count('_')
        res=[]
        n=0
        for item in possiblePattern:
            if item.count('_')==numSepFilename:
                if self.debug!=0:
                    print "   possible pattern[%s]:%s" % (n,item)
                res.append(item)
                n=n+1

        return res
        

    #
    # get an element of the filename, giving the pattern block
    #
    def getFilenameElement(self, fileName, patterm, patternBlock):
        tmp=patterm.replace('<','').replace('>','')
        print "##### get patternBlock %s on fileName=%s; pattern=%s" % (patternBlock,fileName,tmp) 
        pos=tmp.find(patternBlock)
        print "##### POS=%s" % pos
        if pos<0:
            raise Exception("pattern block not found:%s in pattern:%s" % (patternBlock, patterm))
        pos2=pos+len(patternBlock)
        print "##### POS2=%s" % pos2
        return fileName[pos:pos2]


    #
    #
    #
    def toString(self):
        out=StringIO()
        print >>out, "NamingConvention\n"
        print >>out, " usedBase:%s\n" % self.usedBase
        print >>out, " usedPattern:%s\n" % self.usedPattern
        print >>out, " possible instance pattern:\n"
        n=0
        for item in self.possible_pattern:
            print >>out, "   %s\n" % item
            n=n+1
        return out.getvalue()

    #
    #
    #

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        n=NamingConvention()

        print "namingConvention dump:%s" % n.toString()
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


        if not isinstance(n, NamingConvention):
            print "instance not recognized"
            
    except Exception, err:
        log.exception('Error from throws():')

