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
    # the mapping of nodes used in xml report. keys is node path
    xmlNodeUsedMapping={}
     
    def __init__(self):
            print ' init Base_Metadata done'


    #@abstractmethod
    def setUsedInXmlMap(self, adict):
        self.xmlNodeUsedMapping=adict

    def isFieldUsed(self, path=None):
        #print "###########################\n###########################\n isFieldUsed: path:'%s'  len(exclusion):%d" % (path, len(self.xmlNodeUsedMapping))
        #n=0
        #for item in self.xmlNodeUsedMapping.keys():
        #    print "########################### exclusion[%d]:%s=%s." % (n, item, self.xmlNodeUsedMapping[item])
            
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
            

    def dump(self):
        #raise Exception("STOP")
        res='Dict:\n'
        for item in sorted(self.dict.keys()):
            res="%s%s=%s\n" % (res, item, self.dict[item])
        if len(self.xmlNodeUsedMapping.keys())>0:
            res='%s\nXml used mapping:\n' % res
            for item in sorted(self.xmlNodeUsedMapping.keys()):
                res="%s%s=%s\n" % (res, item, self.xmlNodeUsedMapping[item])
        print res
    
    def toString(self):
        res='Dict:\n'
        for item in sorted(self.dict.keys()):
            #print "key:"+item
            res="%s%s=%s\n" % (res, item, self.dict[item])
        if len(self.xmlNodeUsedMapping.keys())>0:
            res='%s\nXml used mapping:\n' % res
            for item in sorted(self.xmlNodeUsedMapping.keys()):
                res="%s%s=%s\n" % (res, item, self.xmlNodeUsedMapping[item])
        return res
