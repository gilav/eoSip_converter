# -*- coding: cp1252 -*-
#
# 
#
#

from esaProducts import metadata



class IndexCreator():
    header=[]
    DEFAULT_HEADERS="File|PLATFORM_SHORT_NAME|INSTRUMENT_SHORT_NAME|OPERATIONAL_MODE|PRODUCT_TYPE|PRODUCT_ID|PARENT_IDENTIFIER|BEGIN_DATE|END_DATE|AVAILABILITY_TIME|PRODUCT_URI|PRODUCT_VERSION|PRODUCT_SIZE|FOOTPRINT|SENSOR_TYPE|PROCESSING_MODE|ACQUISITION_TYPE|STATUS|IMAGE_QUALITY_DEGRADATION|PLATFORM_SERIAL_IDENTIFIER|ORBIT_NUMBER|ORBIT_DIRECTION|WRS_LONGITUDE_GRID|WRS_LATITUED_GRID|ILLUMINATION_AZIMUTH_ANGLE|ILLUMINATION_ZENITH_ANGLE|ILLUMINATION_ELEVATION_ANGLE|CLOUD_COVER_PERCENTAGE|UPPER_LEFT_CLOUD_VOTE|UPPER_RIGHT_CLOUD_VOTE|LOWER_LEFT_CLOUD_VOTE|LOWER_RIGHT_CLOUD_VOTE|BROWSE_METADATA_LOCATION|BROWSE_IMAGE_LOCATION|THUMBNAIL_URL|"
    rows=[]
    #
    debug=0

    def __init__(self, h=None):
        global DEFAULT_HEADERS
        if h==None:
            h=self.DEFAULT_HEADERS
            if self.debug!=0:
                print " using default header"
        toks=h.split("|")
        for item in toks:
            self.header.append(item)
        if self.debug!=0:
                print " IndexCreator init done; number of headers:%s" % len(toks)

    def addOneProduct(self, met=None):
        row.append("a row")
        pass

    def getIndexesText(self):
        res=''
        for item in rows:
            res="%s%s\n" % (res, item)
        return res

    def getOneIndexRow(self, row=0):
        return rows[row]
        
        

    
if __name__ == '__main__':
    pass
