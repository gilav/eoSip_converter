# -*- coding: cp1252 -*-
#
# 
#
#

import sys,traceback

from esaProducts import metadata, browse_metadata



class IndexCreator():
    header=[]
    mapping=[]
    DEFAULT_HEADERS="File|PLATFORM_SHORT_NAME|INSTRUMENT_SHORT_NAME|OPERATIONAL_MODE|PRODUCT_TYPE|PRODUCT_ID|PARENT_IDENTIFIER|BEGIN_DATE|END_DATE|AVAILABILITY_TIME|PRODUCT_URI|PRODUCT_VERSION|PRODUCT_SIZE|FOOTPRINT|SENSOR_TYPE|PROCESSING_MODE|ACQUISITION_TYPE|STATUS|IMAGE_QUALITY_DEGRADATION|PLATFORM_SERIAL_IDENTIFIER|ORBIT_NUMBER|ILLUMINATION_AZIMUTH_ANGLE|ILLUMINATION_ZENITH_ANGLE|ILLUMINATION_ELEVATION_ANGLE|CLOUD_COVER_PERCENTAGE|BROWSE_METADATA_LOCATION|BROWSE_IMAGE_LOCATION|THUMBNAIL_URL|"
    BASE_URL="@BASE_URL@"
    #
    #
    # 
    #
    METADATA_MAPPING={'File':metadata.METADATA_PACKAGENAME,
                      'PLATFORM_SHORT_NAME':metadata.METADATA_PLATFORM,
                      'INSTRUMENT_SHORT_NAME':metadata.METADATA_INSTRUMENT,
                      'OPERATIONAL_MODE':None,
                      'PRODUCT_TYPE':metadata.METADATA_TYPECODE,
                      'PRODUCT_ID':metadata.METADATA_PACKAGENAME,
                      'PARENT_IDENTIFIER':None,
                      'BEGIN_DATE':metadata.METADATA_START_TIME,
                      'END_DATE':metadata.METADATA_STOP_TIME,
                      'AVAILABILITY_TIME':metadata.METADATA_GENERATION_TIME,
                      'PRODUCT_URI':metadata.METADATA_PRODUCTNAME,
                      'PRODUCT_VERSION':metadata.METADATA_VERSION,
                      'PRODUCT_SIZE':metadata.METADATA_PRODUCT_SIZE,
                      'FOOTPRINT':metadata.METADATA_FOOTPRINT,
                      'SENSOR_TYPE':metadata.METADATA_REPORT_TYPE,
                      'PROCESSING_MODE':None,
                      'ACQUISITION_TYPE':None,
                      'STATUS':metadata.METADATA_STATUS,
                      'IMAGE_QUALITY_DEGRADATION':None,
                      'PLATFORM_SERIAL_IDENTIFIER':metadata.METADATA_PLATFORM_ID,
                      'ORBIT_NUMBER':metadata.METADATA_ORBIT,
                      'ORBIT_DIRECTION':metadata.METADATA_ORBIT_DIRECTION,
                      'ILLUMINATION_AZIMUTH_ANGLE':metadata.METADATA_SUN_AZIMUTH,
                      'ILLUMINATION_ZENITH_ANGLE':None,
                      'ILLUMINATION_ELEVATION_ANGLE':metadata.METADATA_SUN_ELEVATION,
                      'CLOUD_COVER_PERCENTAGE':metadata.METADATA_CLOUD_COVERAGE,
                      'BROWSE_METADATA_LOCATION':None,
                      'BROWSE_IMAGE_LOCATION':browse_metadata.BROWSE_METADATA_FILENAME,
                      'THUMBNAIL_URL':browse_metadata.BROWSE_METADATA_FILENAME
                      }
    # metadata taken from browse (not from product)
    BROWSE_METADATA_USED=['BROWSE_METADATA_LOCATION', 'BROWSE_IMAGE_LOCATION', 'THUMBNAIL_URL']

    # metadata taken from browse (not from product) and using the BASE_URL
    BROWSE_METADATA_BASE_URL_USED=['BROWSE_METADATA_LOCATION','BROWSE_IMAGE_LOCATION','THUMBNAIL_URL']
    
    #
    rows=[]
    #
    debug=0


    #
    # added are 'field:mapping' like: 'PARENT_PRODUCT:METADATA_PARENT_PRODUCT'
    #
    def __init__(self, h=None, added=None):
        global DEFAULT_HEADERS,METADATA_MAPPING
        self.header=[]
        self.mapping={}

        # verif
        l1=len(self.DEFAULT_HEADERS.split("|"))
        l2=len(self.METADATA_MAPPING.keys())
        if l1 != l2:
            raise Exception("IndexCreator init problem: different size between field and mapping:%d %d" % (l1, l2))
        
        if h==None: # default headers, + added if anny
            if self.debug>1:
                print " using default header"
            n=0
            for item in self.DEFAULT_HEADERS.split("|"):
                if len(item)>0:
                    if self.debug>1:
                        print " ############# header[%d]:%s" % (n, item)
                    self.header.append(item)
                    n=n+1
            for item in self.METADATA_MAPPING.keys():
                self.mapping[item]=self.METADATA_MAPPING[item]
                if self.debug>1:
                    print " ############# mapping[%d]:%s<==>%s" % (n, item, self.METADATA_MAPPING[item])
                    n=n+1
            # added
            if added!=None:
                if self.debug>1:
                    print " add added to default header"
                for item in added.split("|"):
                    if self.debug>1:
                        print " ############# added header+mapping[%d]:%s" % (n, item)
                    pos=item.find(':')
                    if pos > 0:
                        self.header.append(item[0:pos])
                        self.mapping[item[0:pos]]=item[pos+1:]
                        n=n+1
                    else:
                        raise Exception("invalid added field:mapping, no ':' in:%s" % item)
                        
        else: # specific headers is any, defaults + added if anny
            if h!=None:
                if self.debug>1:
                    print " specific header"
                toks=h.split("|")
                n=0
                for item in toks:
                    if len(item) > 0:
                        if self.debug>1:
                            print " ############# specific header[%d]:%s" % (n, item)
                        self.header.append(item)
                        n=n+1
            n=0
            for item in self.METADATA_MAPPING.keys():
                self.mapping[item]=self.METADATA_MAPPING[item]
                if self.debug>1:
                    print " ############# mapping[%d]:%s<==>%s" % (n, item, self.METADATA_MAPPING[item])
                    n=n+1
                    
            # added
            if added!=None:
                if self.debug>1:
                    print " add added to specific header"
                for item in added.split("|"):
                    if self.debug>1:
                        print " ############# added header[%d]:%s" % (n, item)
                    pos=item.find(':')
                    if pos > 0:
                        self.header.append(item[0:pos])
                        self.mapping[item[0:pos]]=item[pos+1:]
                        n=n+1
                    else:
                        raise Exception("invalid added field:mapping, no ':' in:%s" % item)
        
        if self.debug!=0:
            print " ########################## IndexCreator init done; number of headers:%s, %s" % (n, len(self.header))
        self.rows=[]


    def addOneProduct(self, met=None, bmet=None):
        global BROWSE_METADATA_USED, BASE_URL
        res=''
        n=0
        if self.debug!=0:
            print " ########################## create index row[%s]: len(self.header):%s" % (n, len(self.header))
            print " ## START browse metasdata:"
            n=0
            for key in bmet.dict.keys():
                print " bmet[%s]%s=%s" % (n, key, bmet.dict[key])
                n=n+1
            print " ## END browse metasdata:"
            for item in self.BROWSE_METADATA_USED:
                print " @@@@@@@@@@@@@@@@@@@@ self.BROWSE_METADATA_USED:%s" % item

        
        for field in self.header:
            if self.debug!=0:
                print "  #### create index row: field[%s]:'%s'" % (n,field)
            #key=self.METADATA_MAPPING[field]
            key=self.mapping[field]
            if key==None:
                value='N/A'
            else:
                try:
                    useBrowse=0
                    useBrowseBaseUrl=0
                    try:
                        self.BROWSE_METADATA_USED.index(field)
                        useBrowse=1
                        #print "  #### useBrowse"
                    except:
                        pass

                    try:
                        self.BROWSE_METADATA_BASE_URL_USED.index(field)
                        useBrowseBaseUrl=1
                        #print "  #### useBrowseBaseUrl"
                    except:
                        pass
                    
                    if useBrowse==0:
                        #print "  #### create index row: field[%s]: key=%s: use metadata" % (n,key)
                        value=met.getMetadataValue(key)
                    else:
                        if bmet==None:
                            value="N/A"
                        else:
                            if useBrowseBaseUrl==0:
                                #print "  #### create index row: field[%s]: key=%s: use BROWSE metadata" % (n,key)
                                value=bmet.getMetadataValue(key)
                            else:
                                value="%s%s%s" % (self.BASE_URL, met.getMetadataValue(metadata.METADATA_PRODUCT_RELATIVE_PATH), bmet.getMetadataValue(key))
                except:
                    value="ERROR_getMetadataValue"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())

            if self.debug!=0:
                print "  #### create index row: field[%s]: key=%s" % (n,key)
            if len(res) > 0:
                res="%s|" % res
            res="%s%s" % (res, value)
            if self.debug!=0:
                print "  #### create index row: field[%s]: value=%s" % (n,value)
            n=n+1
        res="%s|" % (res)
            
        self.rows.append(res)


    def getIndexesText(self):
        res=''
        for field in self.header:
            if len(res)>0:
                res="%s|" % res
            res="%s%s" % (res, field)
        res="%s\n" % res
        for item in self.rows:
            res="%s%s\n" % (res, item)
        return res


    def getOneIndexRow(self, row=0):
        return rows[row]
        
        

    
if __name__ == '__main__':
    pass
