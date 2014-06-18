# -*- coding: cp1252 -*-
#
# this class encapsulate the metadata info for products 
#
#
from abc import ABCMeta, abstractmethod
import sys
import traceback
from cStringIO import StringIO
#from definitions_EoSip import sipBuilder
#from sipBuilder import SipBuilder

# type of metadata:
METADATATYPE_PRODUCT='METADATATYPE_PRODUCT'
METADATATYPE_BROWSE='METADATATYPE_BROWSE'
METADATATYPE_BASE='METADATATYPE_BASE'

class Base_Metadata:
    # type of metadata:
    #METADATATYPE_PRODUCT='METADATATYPE_PRODUCT'
    #METADATATYPE_BROWSE='METADATATYPE_BROWSE'
    #METADATATYPE_BASE='METADATATYPE_BASE'
    
    #
    counter=0
    #
    debug=0
    # the metadata dictionnary
    #dict=None
    # the localAttibutes
    #localAttributes=[]
    # the mapping of nodes used in xml report. keys is node path
    xmlNodeUsedMapping={}


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
        print ' init Base_Metadata done'
        


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
    # test if a field is used in the xml report
    #
    def isFieldUsed(self, path=None):
        if self.debug>=2:
            print "###########################\n###########################\n isFieldUsed: path:'%s'  len(exclusion):%d" % (path, len(self.xmlNodeUsedMapping))
        n=0
        for item in self.xmlNodeUsedMapping.keys():
            if self.debug>=2:
                print "########################### exclusion[%d]:%s=%s." % (n, item, self.xmlNodeUsedMapping[item])
            n=n+1
            
        if self.xmlNodeUsedMapping.has_key(path):
            if self.debug>=2:
                print "   field at path:'%s' used flag:%s" % (path, self.xmlNodeUsedMapping[path])
            if self.xmlNodeUsedMapping[path]=='UNUSED':
                if self.debug>=2:
                    print "########################### UNUSED"
                return 0
            else:
                if self.debug>=2:
                    print "########################### USED"
                return 1
        else:
            if self.debug>=2:
                print "########################### NO MAPPING; USED"
                print "  field with path:'%s' has no used map entry" % path
            return 1
            

    #
    #
    #
    def toString(self):
        out=StringIO()
        print >>out, '\n##################################\n#### START Metadata Info #########\n### Dict:'
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
        
