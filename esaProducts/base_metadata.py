# -*- coding: cp1252 -*-
#
# this class encapsulate the metadata info for products 
#
#
from abc import ABCMeta, abstractmethod
import sys
import traceback



class Base_Metadata:
    #
    counter=0
    #
    debug=0
    # the metadata dictionnary
    dict=None
    # the localAttibutes
    localAttributes=[]
    # the mapping of nodes used in xml report. keys is node path
    xmlNodeUsedMapping={}
    # the typology of xml report in use: 'eop:EarthObservation', 'sar:EarthObservation', 'opt:EarthObservation'
    TYPOLOGY_LIST=["eop_EarthObservation", "sar_EarthObservation", "opt_EarthObservation"]
    TYPOLOGY_eop_EarthObservation=0;
    TYPOLOGY_sar_EarthObservation=1;
    TYPOLOGY_opt_EarthObservation=2;
    xmlTypology_used=0


    #
    #
    #
    def __init__(self):
            print ' init Base_Metadata done'


    #
    # use a xml typology
    #
    def useXmlTypology(self, n=TYPOLOGY_eop_EarthObservation):
        if n < len(TYPOLOGY_LIST):
            xmlTypology_used=n
        else:
            raise "typology unknown:%d" % n
        

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
        #print "###########################\n###########################\n isFieldUsed: path:'%s'  len(exclusion):%d" % (path, len(self.xmlNodeUsedMapping))
        n=0
        for item in self.xmlNodeUsedMapping.keys():
            #print "########################### exclusion[%d]:%s=%s." % (n, item, self.xmlNodeUsedMapping[item])
            n=n+1
            
        if self.xmlNodeUsedMapping.has_key(path):
            #print "   field at path:'%s' used flag:%s" % (path, self.xmlNodeUsedMapping[path])
            if self.xmlNodeUsedMapping[path]=='UNUSED':
                #print "########################### UNUSED"
                return 0
            else:
                #print "########################### USED"
                return 1
        else:
            #print "########################### NO MAPPING; USED"
            #print "  field with path:'%s' has no used map entry" % path
            return 1
            

    #
    #
    #
    def dump(self):
        res='Dict:\n'
        for item in sorted(self.dict.keys()):
            res="%s%s=%s\n" % (res, item, self.dict[item])
        if len(self.xmlNodeUsedMapping.keys())>0:
            res='%s\nXml used mapping:\n' % res
            for item in sorted(self.xmlNodeUsedMapping.keys()):
                res="%s%s=%s\n" % (res, item, self.xmlNodeUsedMapping[item])
        print res

    #
    #
    #
    def toString(self):
        res='Dict:\n'
        for item in sorted(self.dict.keys()):
            res="%s%s=%s\n" % (res, item, self.dict[item])
        if len(self.xmlNodeUsedMapping.keys())>0:
            res='%s\nXml used mapping:\n' % res
            for item in sorted(self.xmlNodeUsedMapping.keys()):
                res="%s%s=%s\n" % (res, item, self.xmlNodeUsedMapping[item])
        return res
