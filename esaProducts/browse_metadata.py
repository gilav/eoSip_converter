# -*- coding: cp1252 -*-
#
# this class encapsulate the metadata info for browse 
#
#
import sys
import traceback
import base_metadata
from base_metadata import Base_Metadata
#print "\nbrowse_metadata SYS_PATH:%s" % sys.path
#try:
#import sipBuilder
#except:
#from definitions_EoSip import sipBuilder

#BROWSE_METADATA_BROWSE_CHOICE='BROWSE_METADATA_BROWSE_CHOICE'
BROWSE_METADATA_IDENTIFIER='BROWSE_METADATA_IDENTIFIER'
BROWSE_METADATA_FILENAME='BROWSE_METADATA_FILENAME'
BROWSE_METADATA_NAME='BROWSE_METADATA_NAME'
BROWSE_METADATA_REPORT_NAME='BROWSE_METADATA_REPORT_NAME'
BROWSE_METADATA_IMAGE_TYPE='BROWSE_METADATA_IMAGE_TYPE'
BROWSE_METADATA_IMAGE_RESOLUTION='BROWSE_METADATA_IMAGE_RESOLUTION'
BROWSE_METADATA_START_DATE='BROWSE_METADATA_START_DATE'
BROWSE_METADATA_START_TIME='BROWSE_METADATA_START_TIME'
BROWSE_METADATA_STOP_DATE='BROWSE_METADATA_STOP_DATE'
BROWSE_METADATA_STOP_TIME='BROWSE_METADATA_STOP_TIME'
BROWSE_METADATA_BROWSE_TYPE='BROWSE_METADATA_BROWSE_TYPE'
BROWSE_METADATA_RECT_COORDLIST='BROWSE_METADATA_RECT_COORDLIST'
BROWSE_METADATA_FOOTPRINT_NUMBER_NODES='BROWSE_METADATA_FOOTPRINT_NUMBER_NODES'
BROWSE_METADATA_BROWSE_CHOICE='BROWSE_METADATA_BROWSE_CHOICE'


class Browse_Metadata(Base_Metadata):
    
    METADATA_FIELDS=[BROWSE_METADATA_IDENTIFIER, BROWSE_METADATA_FILENAME, BROWSE_METADATA_IMAGE_TYPE,
                     BROWSE_METADATA_START_DATE, BROWSE_METADATA_START_TIME,
                     BROWSE_METADATA_STOP_DATE, BROWSE_METADATA_STOP_TIME, BROWSE_METADATA_BROWSE_TYPE]


    
    def __init__(self, defaults=None):
        Base_Metadata.__init__(self)
        self.dict['__METADATATYPE__']=base_metadata.METADATATYPE_BROWSE
        for item in self.METADATA_FIELDS:
            self.dict[item] = None
        if defaults!=None:
            for item in defaults.iterkeys():
                self.dict[item] = defaults[item]
        print ' init Browse_Metadata done'


        
    def eval(self, expr):
        try:
            if not expr[0:5] == 'self.':
                expr="self.%s" % (expr)
            res=eval(expr)
        except:
            xc_type, exc_obj, exc_tb = sys.exc_info()
            res="%s%s%s" % (xc_type, exc_obj, exc_tb)
            traceback.print_exc(file=sys.stdout)
        return res


    def getMetadataNames(self):
        res=[]
        # copy defaults fieds
        for item in self.dict.iterkeys():
            res.append(item)
        # add extra fields
        return res


    def setMetadataPair(self, name=None, value=None):
        self.dict[name]=value


    def getMetadataValue(self,name=None):
        if self.dict.has_key(name):
            return self.dict[name]
        else:
            return sipBuilder.VALUE_NOT_PRESENT
            #return "NOT-PRESENT"


    def getNextCounter(self):
        self.counter=self.counter+1
        return self.counter




    
if __name__ == '__main__':
    met=Browse_Metadata()
    met.dump()
    met.setMetadataPair('a','aaa')
    print "set a=aaa"
    met.dump()
    print "get a:%s" % met.getMetadataValue('a')
    print "get b:%s" % met.getMetadataValue('b')
