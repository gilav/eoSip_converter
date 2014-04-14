# -*- coding: cp1252 -*-
#
# this class represent a Dimap Spot product (ZIP directory product)
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

class Dimap_Spot_Product(Directory_Product):

    PREVIEW_NAME='preview.jpg'
    METADATA_NAME='metadata.dim'
    EXTRACTED_PATH=None
    debug=0
    #



    xmlMapping={metadata.METADATA_START_DATE:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE',
                metadata.METADATA_START_TIME:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME',
                metadata.METADATA_PROCESSING_TIME:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_PROCESSING_CENTER:'Production/Production_Facility/PROCESSING_CENTER',
                metadata.METADATA_SOFTWARE_NAME:'Production/Production_Facility/SOFTWARE_NAME',
                metadata.METADATA_SOFTWARE_VERSION:'Production/Production_Facility/SOFTWARE_VERSION',
                metadata.METADATA_DATASET_NAME:'Dataset_Id/DATASET_NAME',
                metadata.METADATA_PLATFORM:'Dataset_Sources/Source_Information/Scene_Source/MISSION',
                metadata.METADATA_PLATFORM_ID:'Dataset_Sources/Source_Information/Scene_Source/MISSION_INDEX',
                metadata.METADATA_INSTRUMENT:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_INSTRUMENT_ID:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX',
                metadata.METADATA_SENSOR_NAME:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_SENSOR_CODE:'Dataset_Sources/Source_Information/Scene_Source/SENSOR_CODE',
                metadata.METADATA_DATA_FILE_PATH:'Data_Access/Data_File/DATA_FILE_PATH@href',
                metadata.METADATA_DATASET_PRODUCTION_DATE:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE',
                metadata.METADATA_VIEWING_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/VIEWING_ANGLE',
                metadata.METADATA_SUN_AZIMUTH:'Dataset_Sources/Source_Information/Scene_Source/SUN_AZIMUTH',
                metadata.METADATA_SUN_ELEVATION:'Dataset_Sources/Source_Information/Scene_Source/SUN_ELEVATION',
                metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER:'Coordinate_Reference_System/Horizontal_CS/HORIZONTAL_CS_CODE'
                }
    
    def myInit(self):
        #if self.debug!=0:
        print " init class Dimap_Spot_Product"
        self.type=Product.TYPE_DIR
        self.preview_data=None
        self.meatadata_data=None
        self.preview_path=None
        self.metadata_path=None
        self.PREVIEW_NAME='preview.jpg'
        self.METADATA_NAME='metadata.dim'
        
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
            if name.find(self.PREVIEW_NAME)>=0:
                self.preview_path="%s/%s" % (folder, name)
            elif name.find(self.METADATA_NAME)>=0:
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

    def buildTypeCode_(self):
        #global product_type_dict
        my_product_type = self.product_type_dict[self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)][self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)][self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)]
        print "############################## %s" % my_product_type
        self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,my_product_type)

    def buildTypeCode(self):
        if (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='HRV'):
            #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ HRV"
            if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='P':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV1_P__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='P':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV2_P__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='X':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV1_X__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='X':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV_X__1P')
            else:
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV#_#_##')
                        
        elif (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='HRVIR'):
            #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ HRVIR"
            if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='M':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV1_P__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='M':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV2_P__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='I' or self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='X'):
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRI1_X__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='I' or self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='X'):
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRI2_X__1P')
            else:
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRVI_#_##')

        elif (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='HRG'):
            #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ HRG"
            if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='J':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG1_X__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='J':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG2_X__1P')
            else:
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG#_#_##')

        else:
            raise Exception("Product type UNKNOWN")

       
    def extractMetadata(self, met=None):
        self.debug=1
        if met==None:
            raise Exception("metadate is None")

        # set some evident values
        met.setMetadataPair(metadata.METADATA_PRODUCTNAME, self.origName)
        
        # use what contains the metadata file
        metContent=self.getMetadataInfo()
        
        # extact metadata
        helper=xmlHelper.XmlHelper()
        #helper.setDebug(1)
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
        #raise Exception("STOP")

        # convert sun azimut from EEE format
        tmp = self.metadata.getMetadataValue(metadata.METADATA_SUN_AZIMUTH)
        self.metadata.setMetadataPair(metadata.METADATA_SUN_AZIMUTH, formatUtils.EEEtoNumber(tmp))

        tmp = self.metadata.getMetadataValue(metadata.METADATA_SUN_ELEVATION)
        self.metadata.setMetadataPair(metadata.METADATA_SUN_ELEVATION, formatUtils.EEEtoNumber(tmp))
        
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
        result=""
        nodes=[]
        helper.setDebug(1)
        helper.getNodeByPath(None, 'Dataset_Frame', None, nodes)
        if len(nodes)==1:
            vertexList=helper.getNodeChildrenByName(nodes[0], 'Vertex')
            if len(vertexList)==0:
                raise Exception("can not find footprint vertex")

            n=0
            closePoint=""
            for node in vertexList:
                lon = helper.getNodeText(helper.getFirstNodeByPath(node, 'FRAME_LON', None))
                lat = helper.getNodeText(helper.getFirstNodeByPath(node, 'FRAME_LAT', None))
                if self.debug!=0:
                    print "  ############# vertex %d: lon:%s  lat:%s" % (n, lon, lat)
                if len(result)>0:
                    result="%s " % (result)
                result="%s%s %s" % (result, formatUtils.EEEtoNumber(lat), formatUtils.EEEtoNumber(lon))
                if n==0:
                    closePoint = "%s %s" % (formatUtils.EEEtoNumber(lat), formatUtils.EEEtoNumber(lon))
                n=n+1
            result="%s %s" % (result,closePoint)
                
            #raise Exception("STOP")

            # store it for browse report in rectified browse
            # should be in lower left lat/lon + upper right lat/lon.
            #met.setMetadataPair(browse_metadata.BROWSE_METADATA_RECT_COORDLIST, "%s %s %s %s" % (bry, ulx, uly , brx))
            if self.debug!=0:
                print "  ############# footprint:%s" % (result)
            if self.debug!=0:
                print "  ############# ccw:%s" % (formatUtils.reverseFootprint(result))
            met.setMetadataPair(metadata.METADATA_FOOTPRINT, formatUtils.reverseFootprint(result))
            
            #raise Exception("STOP")
        return result
        

    def toString(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        return res


    def dump(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        print res


if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=Dimap_Product("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.getMetadataInfo()
    except Exception, err:
        log.exception('Error from throws():')
