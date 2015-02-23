# -*- coding: cp1252 -*-
#
# this class encapsulate the metadata info for products 
#
#
from abc import ABCMeta, abstractmethod
import sys
import traceback
from cStringIO import StringIO
import definitions_EoSip
import sipBuilder


# type of metadata:
METADATATYPE_PRODUCT='METADATATYPE_PRODUCT'
METADATATYPE_BROWSE='METADATATYPE_BROWSE'
METADATATYPE_BASE='METADATATYPE_BASE'

class Base_Metadata:
    
    #
    counter=0
    
    #
    debug=1
    
    # the mapping of nodes used in xml report. keys is node path
    xmlNodeUsedMapping={}

    # the mapping of nodes used in xml report. keys is node path
    xmlVarnameMapping={}
    
    
    #
    #
    #
    def __init__(self):
        global METADATATYPE_BASE
        # metadata dictionnary
        self.dict={}
        self.dict['__METADATATYPE__']=METADATATYPE_BASE
        # a counter, can be used to increment the gml_id in the xml reports
        self.counter=0
        # other info
        self.otherInfo={}
        # the localAttibutes
        self.localAttributes=[]
        self.label='no label'
        self.defined=False
        
        print ' init Base_Metadata done'


    #
    # tells if the metadata are defined. used to prevent to set everything to None
    #
    def isMetadataDefined(self):
        return self.defined
        
    #
    # set if the metadata are defined.
    #
    def setMetadataDefined(self, b):
        self.defined = b

    
    #
    #
    #
    def alterMetadataMaping(self, key, value):
        #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ will alterMetadataMaping for: key=%s  mapping=%s" % (key, value)
        self.xmlVarnameMapping[key]=value
    #
    #
    #
    def isMetadataMapingAltered(self):
        return len(self.xmlVarnameMapping.keys())>0
    #
    #
    #
    def getMetadataMaping(self, key, origMappingMap):
        #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ origMappingMap:%s" % (origMappingMap)
        if self.xmlVarnameMapping.has_key(key):
            return self.xmlVarnameMapping[key]
        else:
            if origMappingMap.has_key(key):
                return origMappingMap[key]
            else:
                return None
    #
    #
    #
    def setOtherInfo(self, key, value):
        self.otherInfo[key]=value


    #
    #
    #
    def getOtherInfo(self, key):
        return self.otherInfo[key]
    

    #
    # add a local attributes
    #
    def addLocalAttribute(self, name, value):
        adict={}
        adict[name]=value
        self.localAttributes.append(adict)


    #
    # get the local attributes
    #
    def getLocalAttribute(self):
        return self.localAttributes

    
    #
    # set the dictionnary of node used in the xml reports
    #
    def setUsedInXmlMap(self, adict):
        self.xmlNodeUsedMapping=adict

    #
    # get the dictionnary of node used in the xml reports
    #
    def getUsedInXmlMap(self):
        return self.xmlNodeUsedMapping


    #
    # test if a field is used in the xml report
    #
    def isFieldUsed(self, path=None, aDebug=0):
        if self.debug>=2 or aDebug!=0:
            print "###########################\n###########################\n isFieldUsed: path:'%s'  len(exclusion):%d" % (path, len(self.xmlNodeUsedMapping))
        n=0
        for item in self.xmlNodeUsedMapping.keys():
            if self.debug>=2 or aDebug!=0:
                print "########################### exclusion[%d]:%s=%s." % (n, item, self.xmlNodeUsedMapping[item])
            n=n+1
            
        if self.xmlNodeUsedMapping.has_key(path):
            if self.debug>=2 or aDebug!=0:
                print "   field at path:'%s' used flag:%s" % (path, self.xmlNodeUsedMapping[path])
            if self.xmlNodeUsedMapping[path]=='UNUSED':
                if self.debug>=2 or aDebug!=0:
                    print "########################### UNUSED"
                return 0
            else:
                if self.debug>=2 or aDebug!=0:
                    print "########################### USED"
                return 1
        else:
            if self.debug>=2 or aDebug!=0:
                print "########################### NO MAPPING; USED"
                print "  field with path:'%s' has no used map entry" % path
            return 1
            
    #
    #
    #
    def getMetadataNames(self):
        return sorted(self.dict.keys())
    
    #
    #
    #
    def setMetadataPair(self, name=None, value=None):
        self.dict[name] = value

    #
    #
    #
    def getMetadataValue(self,name=None):
        if self.dict.has_key(name):
            return self.dict[name]
        else:
            return sipBuilder.VALUE_NOT_PRESENT

    #
    #
    #
    def toString(self):
        out=StringIO()
        print >>out, '\n##################################\n#### START Metadata Info #########\n### Label:%s\n### Dict:' % self.label
        for item in sorted(self.dict.keys()):
            print >>out, "%s=%s" % (item, self.dict[item])
        if len(self.xmlNodeUsedMapping.keys())>0:
            print >>out, "\n### Xml used mapping:"
            for item in sorted(self.xmlNodeUsedMapping.keys()):
                print >>out, "%s=%s" % (item, self.xmlNodeUsedMapping[item])
        print >>out, "#### END Metadata Info ###########\n##################################"
        return out.getvalue()


    #
    #
    #
    def dump(self):
        print self.toString()
        
