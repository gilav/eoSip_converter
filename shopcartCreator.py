# -*- coding: cp1252 -*-
#
# 
#
#

import sys,traceback

from esaProducts import metadata, browse_metadata
from esaProducts import definitions_EoSip
from definitions_EoSip import sipBuilder, sipMessageBuilder
from tagResolver import TagResolver


class ShopcartCreator(TagResolver):
    header=[]
    mapping=[]
    DEFAULT_HEADERS="Id|Mission|Sensor|Product|COLLECTION|Status|Start|Stop|Orbit|Track|Frame|Swath|Station|Processing Level|Original Name|Product Id|PASSTIME|Pass|SCENE_CENTER|BBOX|FOOTPRINT|ACQUISITIONDESCRIPTOR|THUMBNAIL_URL|PRODUCT_URL|PRODUCT_TYPE|CLOUD_COVER_PERCENTAGE|SNOW_COVER_PERCENTAGE|IMAGE_QUALITY_DEGRATATION|Display|Mosaic|ORDEROPTIONS|Medium|Delivery|Processing Options|Programming Options|Scene Type|Scene Start|Scene Stop|Scene centre|Selected Frame|Order|SCENE_FOOTPRINT"
    BASE_BROWSE_URL="%BASE_BROWSE_URL%"
    BASE_URL="%BASE_URL%"
    #
    #
    # 
    #
    METADATA_MAPPING={'Id':'$$self.add()$$',
                      'Mission':'@METADATA_PLATFORM@-@METADATA_PLATFORM_ID@',
                      'Sensor':'@METADATA_INSTRUMENT@',
                      'Product':'@METADATA_TYPECODE@',
                      'COLLECTION':'ESA.EECF.SPOT_ESA_MULTI',
                      'Status':'Archived',
                      'Start':'@METADATA_START_DATE@ @METADATA_START_TIME@',
                      'Stop':'@METADATA_STOP_DATE@ @METADATA_STOP_TIME@',
                      'Orbit':'@METADATA_ORBIT@',
                      'Track':'@metadata.METADATA_TRACK@',
                      'Frame':'@metadata.METADATA_FRAME@',
                      'Swath':'',
                      'Station':'',
                      'Processing Level':'@METADATA_PROCESSING_LEVEL@',
                      'Original Name':'@METADATA_ORIGINAL_NAME@',
                      'Product Id':'@METADATA_PRODUCT_ID@',
                      'PASSTIME':'',
                      'Pass':'D',
                      'SCENE_CENTER':'@METADATA_SCENE_CENTER@',
                      'BBOX':'@METADATA_BOUNDING_BOX_CW_CLOSED@',
                      'FOOTPRINT':'@METADATA_FOOTPRINT_CW@',
                      'ACQUISITIONDESCRIPTOR':'ACQ',
                      'THUMBNAIL_URL':'http://172.19.17.85/Spot/@METADATA_PRODUCT_RELATIVE_PATH@/@BROWSE_METADATA_FILENAME@',
                      'PRODUCT_URL':'http://172.19.17.85/Spot/@METADATA_PRODUCT_RELATIVE_PATH@/@METADATA_PRODUCTNAME@',
                      'PRODUCT_TYPE':'@METADATA_TYPECODE@',
                      'CLOUD_COVER_PERCENTAGE':'@METADATA_CLOUD_COVERAGE@',
                      'SNOW_COVER_PERCENTAGE':'',
                      'IMAGE_QUALITY_DEGRATATION':'',
                      'Display':'',
                      'Mosaic':'',
                      'ORDEROPTIONS':'',
                      'Medium':'',
                      'Delivery':'',
                      'Processing Options':'ESA##ESA.EO2##SpotLevel1Aproducts####################',
                      'Programming Options':'',
                      'Scene Type':'',
                      'Scene Start':'',
                      'Scene Stop':'',
                      'Scene centre':'',
                      'Selected Frame':'',
                      'Order':'false',
                      'SCENE_FOOTPRINT':'',
                      }
    # metadata taken from browse (not from product)
    BROWSE_METADATA_USED=['THUMBNAIL_URL']

    # metadata taken from browse (not from product) and using the BASE_URL
    BROWSE_METADATA_BASE_URL_USED=['THUMBNAIL_URL']
    
    #
    rows=[]
    #
    debug=0


    def add(self):
         self.counter=self.counter+1
         return self.counter


    #
    # added are 'field:mapping' like: 'PARENT_PRODUCT:METADATA_PARENT_PRODUCT'
    #
    def __init__(self, h=None, added=None):
        global DEFAULT_HEADERS,METADATA_MAPPING
        self.header=[]
        self.mapping={}

        #
        self.counter=0

        # verif
        l1=len(self.DEFAULT_HEADERS.split("|"))
        l2=len(self.METADATA_MAPPING.keys())
        if l1 != l2:
            raise Exception("ShopcartCreator init problem: different size between field and mapping:%d %d" % (l1, l2))
        
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

    #
    #
    #
    def setMapping(self, key, expr):
        if not self.DEFAULT_HEADERS.has_key(key):
            raise Exception("shopcart header not found:%s" % key)
        self.METADATA_MAPPING[key]=expr
        


    #
    #
    #
    def addOneProduct(self, met=None, bmet=None):
        global BROWSE_METADATA_USED, BASE_URL
        res=''
        n=0
        if self.debug!=0:
            print " ########################## create index row[%s]: len(self.header):%s" % (n, len(self.header))
            if bmet!=None:
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
                print "  #### create shopcart row: field[%s]:'%s'" % (n,field)
            expr=self.mapping[field]
            if expr==None:
                if field!='Id':
                    value='N/A'
                else:
                    value=len(self.rows)+1
            else:
                try:
                    value=self.resolve(expr, met, bmet)
                    if value==sipBuilder.VALUE_NOT_PRESENT:
                        value=''
                    if value=='N/A':
                        value=''
                    if value=='None':
                        value=''
                except:
                    value="ERROR_resolve"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())

            if self.debug!=0:
                print "  #### create shopcart row: field[%s]: expr=%s" % (n,expr)
            if len(res) > 0:
                res="%s|" % res
            res="%s%s" % (res, value)
            if self.debug!=0:
                print "  #### create shopcart row: field[%s]: value=%s" % (n,value)
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

    def getSize(self):
        return len(self.rows)

    def getOneIndexRow(self, row=0):
        return self.rows[row]
        
        

    
if __name__ == '__main__':
    sc=ShopcartCreator()
    met=metadata.Metadata()
    met.setMetadataPair(metadata.METADATA_PLATFORM, "SPOT")
    met.setMetadataPair(metadata.METADATA_PLATFORM_ID, "4")
    met.setMetadataPair(metadata.METADATA_INSTRUMENT, "HRVIR")
    met.setMetadataPair(metadata.METADATA_START_DATE, "2007-05-26")
    met.setMetadataPair(metadata.METADATA_START_TIME, '11:33:36.488');
    met.setMetadataPair(metadata.METADATA_STOP_DATE, "2007-05-26")
    met.setMetadataPair(metadata.METADATA_STOP_TIME, '11:33:43.488');
    
    met.setMetadataPair(metadata.METADATA_FOOTPRINT, "43.505158383 -9.7328153269 43.505158383 -9.7328153269")
    met.setMetadataPair(metadata.METADATA_SCENE_CENTER, "43.505158383 -9.7328153269")
    met.setMetadataPair(metadata.METADATA_CLOUD_COVERAGE, "1")
    met.setMetadataPair(metadata.METADATA_ORBIT_DIRECTION, "DESCENDING")

    bmet=browse_metadata.Browse_Metadata()
    bmet.setMetadataPair(browse_metadata.BROWSE_METADATA_FILENAME, "SP4_OPER_HRI1_X__1P_20070526T113336_20070526T113345_000327_0020_0263.BI.JPG")

    
    sc.addOneProduct(met, bmet)
    print "shopcart:\n%s" % sc.getIndexesText()



    
