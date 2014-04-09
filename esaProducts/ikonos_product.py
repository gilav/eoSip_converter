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

class Ikonos_Product(Directory_Product):

    PREVIEW_SUFFIX='ovr.jpg'
    METADATA_SUFFIX='metadata.txt'
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
        
        n=0
        d=0
        for name in z.namelist():
            n=n+1
            print "  zip content[%d]:%s" % (n, name)
            if name.find(self.PREVIEW_SUFFIX)>=0:
                self.preview_path="%s/%s" % (folder, name)
            elif name.find(self.METADATA_SUFFIX)>=0:
                self.metadata_path="%s/%s" % (folder, name)
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
        self.buildTypeCode()
        return 1


    def extractQuality(self, helper, met):
        return


    #
    # extract the footprint posList point, ccw, lat lon
    #
    def extractFootprint(self, helper, met):
        return
        

    def toString(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        return res


    def dump(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        print res


