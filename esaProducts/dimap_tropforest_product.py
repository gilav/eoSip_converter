# -*- coding: cp1252 -*-
#
# this class represent a Dimap Tropforest product (ZIP directory product)
# as for tropforest products
#  it contains:
#  - a .tif
#  - a .XML metadata file
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

class Dimap_Tropforest_Product(Directory_Product):

    TIF_FILE_SUFFIX='.tif'
    XML_FILE_SUFFIX='.XML'
    TIF_FILE_NAME=None
    XML_FILE_NAME=None
    EXTRACTED_PATH=None
    debug=0
    #

    xmlMapping={metadata.METADATA_START_DATE:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE',
                metadata.METADATA_START_TIME:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME',
                metadata.METADATA_PROCESSING_TIME:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_DATASET_NAME:'Dataset_Id/DATASET_NAME',
                metadata.METADATA_PLATFORM:'Dataset_Sources/Source_Information/Scene_Source/MISSION',
                metadata.METADATA_PLATFORM_ID:'Dataset_Sources/Source_Information/Scene_Source/MISSION_INDEX',
                metadata.METADATA_INSTRUMENT:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_INSTRUMENT_ID:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX',
                metadata.METADATA_SENSOR_NAME:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_SENSOR_CODE:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX',
                metadata.METADATA_DATA_FILE_PATH:'Data_Access/Data_File/DATA_FILE_PATH@href',
                metadata.METADATA_DATASET_PRODUCTION_DATE:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_INCIDENCE_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE',
                metadata.METADATA_VIEWING_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/VIEWING_ANGLE',
                metadata.METADATA_SUN_AZIMUTH:'Dataset_Sources/Source_Information/Scene_Source/SUN_AZIMUTH',
                metadata.METADATA_SUN_ELEVATION:'Dataset_Sources/Source_Information/Scene_Source/SUN_ELEVATION',
                metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER:'Coordinate_Reference_System/Horizontal_CS/HORIZONTAL_CS_CODE'
                }

    def myInit(self):
        #if self.debug!=0:
        print " init class Dimap_Tropforest_Product"
        self.type=Product.TYPE_DIR

    def getMetadataInfo(self):
        if self.XML_FILE_NAME==None:
            raise Exception(" no metadata file")
        if self.debug!=0:
            print " metadata source file:%s" % self.EXTRACTED_PATH+'/'+self.XML_FILE_NAME
        fd=open(self.EXTRACTED_PATH+'/'+self.XML_FILE_NAME, 'r')
        data=fd.read()
        fd.close()
        if self.debug!=0:
            print " extract metadata from:%s" % data
        return data


    def extractToPath(self, folder=None):
        if not os.path.exists(folder):
            raise Exception("destination fodler does not exists:%s" % folder)
        if self.debug!=0:
            print " will exttact product to path:%s" % folder
        fh = open(self.path, 'rb')
        z = zipfile.ZipFile(fh)
        
        n=0
        for name in z.namelist():
            n=n+1
            if self.debug!=0:
                print "  extract[%d]:%s" % (n, name)
            outfile = open(folder+'/'+name, 'wb')
            outfile.write(z.read(name))
            outfile.close()
            if name.find(self.TIF_FILE_SUFFIX)>=0:
                self.TIF_FILE_NAME=name
            elif name.find(self.XML_FILE_SUFFIX)>=0:
                self.XML_FILE_NAME=name       
            if self.debug!=0:
                print "   %s extracted at path:%s" % (name, folder+'/'+name)
        fh.close()
        self.EXTRACTED_PATH=folder


    def extractProductFileSize(self):
        full_path=self.EXTRACTED_PATH+'/'+self.TIF_FILE_NAME
        size=os.stat(full_path).st_size
        return size


    def extractGridFromFile(self,value):
        if value==None:
            raise Exception("value (lat/lon) is None")
        pos=self.TIF_FILE_NAME.find('-')
        if pos>0:
            grid=self.TIF_FILE_NAME.split('_')[0]
            if value=="lat":
                grid_final=grid.split('-')[0]
            elif value=="lon":
                grid_final=grid.split('-')[1]
        else:
            grid=self.TIF_FILE_NAME.split('_')
            if value=="lat":
                grid_final=grid[0]
            elif value=="lon":
                grid_final=grid[1]
        return grid_final


    def extractGridFromFileNormalised(self,value):
        if value==None:
            raise Exception("value (lat/lon) is None")
        grid_final=self.extractGridFromFile(value)
        grid_final=grid_final[0]+grid_final[1:].rjust(3,"0")
        return grid_final


    def buildTypeCode(self):
        if self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='AVNIR':
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'AV2_OBS_11')
        elif self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='SLIM-6-22':
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'SL6_L1R_1P') # or SL6_L1T_1P
        elif self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)==None:
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'EOC_PAN_1G') # or 1P 1R
        else:
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'###_###_##')

       
    def extractMetadata(self, met=None):
        if met==None:
            raise Exception("metadate is None")

        # set some evident values
        met.setMetadataPair(metadata.METADATA_PRODUCTNAME, self.origName)
        
        # use what contains the metadata file
        metContent=self.getMetadataInfo()
        
        # extact metadata
        helper=xmlHelper.XmlHelper()
        helper.setData(metContent);
        helper.parseData()

        #get fields
        resultList=[]
        op_element = helper.getRootNode()
        num_added=0
        
        for field in self.xmlMapping:
            if self.xmlMapping[field].find("@")>=0:
                attr=self.xmlMapping[field].split('@')[1]
                path=self.xmlMapping[field].split('@')[0]
            else:
                attr=None
                path=self.xmlMapping[field]

            aData = helper.getFirstNodeByPath(None, path, None)
            if aData==None:
                aValue=None
            else:
                if attr==None:
                    aValue=helper.getNodeText(aData)
                else:
                    aValue=helper.getNodeAttributeText(aData,attr)        

            if self.debug!=0:
                print "  -->%s=%s" % (field, aValue)
            met.setMetadataPair(field, aValue)
            num_added=num_added+1
            
        self.metadata=met

        self.extractQuality(helper, met)

        self.extractFootprint(helper, met)
                            
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
        #
        if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM)=='ALOS':
            self.metadata.setMetadataPair(metadata.METADATA_PLATFORM_ID, '1')
        elif self.metadata.getMetadataValue(metadata.METADATA_PLATFORM)=='KOMPSAT':
            if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM_ID)==None:
                self.metadata.setMetadataPair(metadata.METADATA_PLATFORM_ID, '2')
        elif self.metadata.getMetadataValue(metadata.METADATA_PLATFORM)=='Deimos':
            if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM_ID)==None:
                self.metadata.setMetadataPair(metadata.METADATA_PLATFORM_ID, '1')

        # add time 00:00:00 to processing time if needed
        tmp = self.metadata.getMetadataValue(metadata.METADATA_PROCESSING_TIME)
        if len(tmp) == 10:
            self.metadata.setMetadataPair(metadata.METADATA_PROCESSING_TIME, "%sT00:00:00Z" % tmp)
            
        # 
        self.buildTypeCode() 


    def extractQuality(self, helper, met):
        #helper.setDebug(1)
        quality=[]
        helper.getNodeByPath(None, 'Quality_Assesment/Quality_Parameter/QUALITY_PARAMETER_DESC', None, quality)
        index=-1
        n=0
        for item in quality:
            #print "############@@@@@@@@@@@@@@@@@ quality[%d]=%s" % (n, helper.getNodeText(item))
            if helper.getNodeText(item)=='QC2 - % Clouds':
                index=n
            n=n+1
        #print "############@@@@@@@@@@@@@@@@@ want quality value at index:%d" % index

        
        quality=[]
        qualityValue=None
        helper.getNodeByPath(None, 'Quality_Assesment/Quality_Parameter/QUALITY_PARAMETER_VALUE', None, quality)
        #print "############@@@@@@@@@@@@@@@@@ quality=%d" % len(quality)
        n=0;
        for item in quality:
            #print "############@@@@@@@@@@@@@@@@@ quality[%d]=%s" % (n, helper.getNodeText(item))
            if index==n:
                qualityValue=helper.getNodeText(item)
            n=n+1
        #print "############@@@@@@@@@@@@@@@@@ cloud qualityValue=%s" % (qualityValue)
        met.setMetadataPair(metadata.METADATA_CLOUD_COVERAGE, qualityValue)
        return 1


    #
    # extract the footprint posList point, ccw, lat lon
    #
    def extractFootprint(self, helper, met):
        nodes=[]
        helper.getNodeByPath(None, 'Geoposition/Geoposition_Insert', None, nodes)
        if len(nodes)==1:
            ulx = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'ULXMAP', None))
            uly = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'ULYMAP', None))
            brx = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'BRXMAP', None))
            bry = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'BRYMAP', None))
            if self.debug!=0:
                print " ulx:%s  uly:%s  brx:%s  bry:%s" % (ulx, uly, brx, bry)
            # store it for browse report in rectified browse
            # should be in lower left lat/lon + upper right lat/lon.
            met.setMetadataPair(browse_metadata.BROWSE_METADATA_RECT_COORDLIST, "%s %s %s %s" % (bry, ulx, uly , brx))

            # make the product metadata report footprint in ccw order
            ccw="%s %s %s %s %s %s %s %s %s %s" % (uly, ulx,   bry, ulx,   bry, brx,   uly, brx,   uly, ulx)
            if self.debug!=0:
                print " posList:%s" % ccw
            met.setMetadataPair(metadata.METADATA_FOOTPRINT, ccw)
        else:
            print " ERROR: Geoposition/Geoposition_Insert has not 4 subnodes:%d" % len(nodes)
        return
        

    def toString(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        return res


    def dump(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        print res


