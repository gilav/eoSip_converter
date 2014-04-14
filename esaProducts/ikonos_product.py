# -*- coding: cp1252 -*-
#
# this class represent a Dimap product (ZIP directory product)
#  it contains:
#
#
#
import os, sys
import logging
import zipfile
import xmlHelper
from product import Product
from directory_product import Directory_Product
import metadata
import browse_metadata
import formatUtils
from sectionIndentedDocument import SectionDocument

class Ikonos_Product(Directory_Product):

    PREVIEW_SUFFIX='ovr.jpg'
    METADATA_SUFFIX='metadata.txt'
    EXTRACTED_PATH=None
    #debug=0
    #

    #
    # syntax is: sectionName|[key][+nLine,+nLine...]
    #
    xmlMapping={metadata.METADATA_START_DATE:'Acquisition Date/Time:*|0',
                metadata.METADATA_SUN_ELEVATION:'Sun Angle Elevation:*|0',
                metadata.METADATA_SUN_AZIMUTH:'Sun Angle Azimuth:*|0',
                metadata.METADATA_INSTRUMENT_ZENITH_ANGLE:'Nominal Collection Azimuth:*|0',
                metadata.METADATA_INSTRUMENT_ELEVATION_ANGLE:'Nominal Collection Elevation:*|0',
                metadata.METADATA_IMAGE_NUM_COLUMNS:'Columns:*|0',
                metadata.METADATA_IMAGE_NUM_ROWS:'Rows:*|0',
                metadata.METADATA_COUNTRY:'Country Code:*|0',
                metadata.METADATA_ACQUISITION_CENTER:'Ground Station ID:*|0',
                metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER:'Map Projection:*|0,2,3',
                metadata.METADATA_CLOUD_COVERAGE:'Percent Cloud Cover:*|0',
                metadata.METADATA_FOOTPRINT:'Component Geographic Corner Coordinates*|3,4,6,7,9,10,12,13,3,4'
                
                }

    def myInit(self):
        #if self.debug!=0:
        print " init class Dimap_Tropforest_Product"
        self.type=Product.TYPE_DIR
        self.preview_data=None
        self.metadata_data=None
        self.preview_path=None
        self.metadata_path=None
        self.PREVIEW_SUFFIX='ovr.jpg'
        self.METADATA_SUFFIX='metadata.txt'

    def getMetadataInfo(self):
        return self.metadata_data


    def extractToPath(self, folder=None):
        global METADATA_NAME,PREVIEW_NAME
        if not os.path.exists(folder):
            raise Exception("destination fodler does not exists:%s" % folder)
        if self.debug!=0:
            print " will exttact product to path:%s" % folder
        fh = open(self.path, 'rb')
        z = zipfile.ZipFile(fh)

        #for DEBUG:
        #self.preview_path='C:/Users/glavaux/Shared/LITE/testData/spaceTmp/workfolder_0/20090721222747_po_2627437_0000000/po_2627437_rgb_0000000_ovr.jpg'
        #self.metadata_path='C:/Users/glavaux/Shared/LITE/testData/spaceTmp/workfolder_0/20090721222747_po_2627437_0000000/po_2627437_metadata.txt'
        #self.EXTRACTED_PATH=folder
        #return

        
        n=0
        d=0
        for name in z.namelist():
            n=n+1
            if self.debug!=0:
                print "  zip content[%d]:%s" % (n, name)
            if name.find(self.PREVIEW_SUFFIX)>=0:
                self.preview_path="%s/%s" % (folder, name)
            elif name.find(self.METADATA_SUFFIX)>=0:
                self.metadata_path="%s/%s" % (folder, name)
            if self.debug!=0:
                print "   %s extracted at path:%s" % (name, folder+'/'+name)
            if name.endswith('/'):
                d=d+1
        if d==1:
            z.extractall(folder)
            fh.close()
            if self.metadata_path!=None:
                fd=open(self.metadata_path, 'r')
                self.metadata_data=fd.read()
                fd.close()
                
            if self.preview_path!=None:
                fd=open(self.preview_path, 'r')
                self.preview_data=fd.read()
                fd.close()
            self.EXTRACTED_PATH=folder
            if self.debug!=0:
                print " ################### self.preview_path:%s" % self.preview_path 
        else:
            raise Exception("More than 1 directory in product:%d" % d)


    def extractProductFileSize(self):
        size=os.stat(self.path).st_size
        return size



    def buildTypeCode(self):
        self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'###_###_##')

       
    def extractMetadata(self, met=None):
        if met==None:
            raise Exception("metadate is None")

        # set some evident values
        met.setMetadataPair(metadata.METADATA_PRODUCTNAME, self.origName)
        
        # use what contains the metadata file
        metContent=self.getMetadataInfo()
        
        # extact metadata, not xml data but 'text section indented'
        sectionDoc = SectionDocument()
        sectionDoc.loadDocument(self.metadata_path)

        #get fields
        num_added=0
        
        for field in self.xmlMapping:
            rule=self.xmlMapping[field]
            aValue=None
            if self.debug==0:
                print " ##### handle metadata:%s" % field

            
            toks=rule.split('|')
            if len(toks)!=2:
                raise Exception("malformed metadata rule:%s" % field)
            # wildcard used?
            if toks[0][-1]=='*':
                line=sectionDoc.getSectionLine(toks[0])
                # line offset(s) list are in second token
                offsets=toks[1].split(',')
                aValue=''
                for offset in offsets:
                    nLine=line+int(offset)
                    if len(aValue)>0:
                        aValue="%s|" % aValue
                    aValue="%s%s" % (aValue,sectionDoc.getLineValue(nLine))
                if self.debug==0:
                    print "  metadata:%s='%s'" % (field, aValue)
            else:
                aValue=sectionDoc.getValue(toks[0], toks[1])
            met.setMetadataPair(field, aValue)
            num_added=num_added+1
            
        self.metadata=met
   
        return num_added


    #
    # refine the metada, should perform in order:
    # - normalise date and time
    # - set platform info
    # - build type code
    #
    def refineMetadata(self):
        # set or verify per mission info
        self.metadata.setMetadataPair('METADATA_SENSOR_TYPE', 'OPTICAL')

        # '2008-08-06 10:51 GMT' into: date + time
        toks=self.metadata.getMetadataValue(metadata.METADATA_START_DATE).strip().split(" ")
        self.metadata.setMetadataPair(metadata.METADATA_START_DATE, toks[0])
        self.metadata.setMetadataPair(metadata.METADATA_START_TIME, "%s:00" % toks[1])
        self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, toks[0])
        self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, "%s:00" % toks[1])

        tmp=self.metadata.getMetadataValue(metadata.METADATA_FOOTPRINT).replace(" degrees","").replace("|","").strip()
        self.metadata.setMetadataPair(metadata.METADATA_FOOTPRINT, formatUtils.reverseFootprint(tmp))

        tmp=self.metadata.getMetadataValue(metadata.METADATA_SUN_ELEVATION).replace(" degrees","").strip()
        self.metadata.setMetadataPair(metadata.METADATA_SUN_ELEVATION, tmp)

        tmp=self.metadata.getMetadataValue(metadata.METADATA_SUN_AZIMUTH).replace(" degrees","").strip()
        self.metadata.setMetadataPair(metadata.METADATA_SUN_AZIMUTH, tmp)

        tmp=self.metadata.getMetadataValue(metadata.METADATA_CLOUD_COVERAGE).strip()
        self.metadata.setMetadataPair(metadata.METADATA_CLOUD_COVERAGE, tmp)
        
        # 
        #self.buildTypeCode()
        return 1


    def extractQuality(self, helper, met):
        return


    #
    # extract the footprint posList point, ccw, lat lon
    #
    def extractFootprint(self, helper, met):
        return
        

    def toString(self):
        res="preview file:%s" % self.preview_path
        res="%s\nmetadata file:%s" % (res, self.metadata_path)
        return res


    def dump(self):
        print self.toString()


