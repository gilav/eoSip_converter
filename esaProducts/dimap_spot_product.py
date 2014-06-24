# -*- coding: cp1252 -*-
#
# this class represent a Dimap Spot product (ZIP directory product)
# as for tropforest products
#  it contains:
#  - a .tif
#  - a .XML metadata file
#
#
import os,sys,sys,inspect
import logging
import zipfile
import xmlHelper
from product import Product
from directory_product import Directory_Product
import metadata
import browse_metadata
import formatUtils
from datetime import datetime, timedelta
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.insert(0,currentdir)
import imageUtil

class Dimap_Spot_Product(Directory_Product):

    PREVIEW_NAME='preview.jpg'
    METADATA_NAME='metadata.dim'
    EXTRACTED_PATH=None
    preview_data=None
    metadata_data=None
    preview_path=None
    metadata_path=None



    xmlMapping={metadata.METADATA_START_DATE:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE',
                metadata.METADATA_START_TIME:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME',
                metadata.METADATA_PROCESSING_TIME:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_PROCESSING_CENTER:'Production/Production_Facility/PROCESSING_CENTER',
                metadata.METADATA_SOFTWARE_NAME:'Production/Production_Facility/SOFTWARE_NAME',
                metadata.METADATA_SOFTWARE_VERSION:'Production/Production_Facility/SOFTWARE_VERSION',
                metadata.METADATA_DATASET_NAME:'Dataset_Id/DATASET_NAME',
                metadata.METADATA_ORBIT:'Dataset_Sources/Source_Information/Scene_Source/Imaging_Parameters/REVOLUTION_NUMBER',
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
                metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER:'Coordinate_Reference_System/Horizontal_CS/HORIZONTAL_CS_CODE',
                metadata.METADATA_SCENE_CENTER_LON:'Dataset_Frame/Scene_Center/FRAME_LON',
                metadata.METADATA_SCENE_CENTER_LAT:'Dataset_Frame/Scene_Center/FRAME_LAT'
                }
    #
    #
    #
    def __init__(self, path):
        Directory_Product.__init__(self, path)
        print " init class Dimap_Spot_Product"

    #
    #
    #
    def getMetadataInfo(self):
        return self.metadata_data

    #
    #
    #
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



    #
    #
    #
    def buildTypeCode(self):
        if (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='HRV'):
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
            if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='J':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG1_X__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='J':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG2_X__1P')
            else:
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG#_#_##')

        else:
            raise Exception("Product type UNKNOWN")

       
    #
    #
    #
    def extractMetadata(self, met=None):
        #self.debug=1
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

        # keep the original product name, add it to local attributes
        met.addLocalAttribute("original_name", self.origName)
                            
        return num_added


    #
    # refine the metada, should perform in order:
    # - normalise date and time
    # - set platform info
    # - build type code
    #
    def refineMetadata(self):
        # processing time: suppress microsec
        tmp = self.metadata.getMetadataValue(metadata.METADATA_PROCESSING_TIME)
        pos = tmp.find('.')
        if pos > 0:
            tmp=tmp[0:pos]
        pos = tmp.find('Z')
        if pos < 0:
            tmp=tmp+"Z"
        self.metadata.setMetadataPair(metadata.METADATA_PROCESSING_TIME, tmp)
        
        # convert sun azimut from EEE format
        tmp = self.metadata.getMetadataValue(metadata.METADATA_SUN_AZIMUTH)
        self.metadata.setMetadataPair(metadata.METADATA_SUN_AZIMUTH, formatUtils.EEEtoNumber(tmp))

        tmp = self.metadata.getMetadataValue(metadata.METADATA_SUN_ELEVATION)
        self.metadata.setMetadataPair(metadata.METADATA_SUN_ELEVATION, formatUtils.EEEtoNumber(tmp))

        tmp = self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE)
        self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE, formatUtils.EEEtoNumber(tmp))

        # fix production date: from 2008-10-01T14:52:01.000000 to 2008-10-01T14:52:01Z
        tmp = self.metadata.getMetadataValue(metadata.METADATA_DATASET_PRODUCTION_DATE)
        pos = tmp.find('.')
        if pos > 0:
            tmp="%sZ" % tmp[0:pos]
        self.metadata.setMetadataPair(metadata.METADATA_DATASET_PRODUCTION_DATE, tmp)

        # set scene center coordinate
        tmp = self.metadata.getMetadataValue(metadata.METADATA_SCENE_CENTER_LON)
        tmp=formatUtils.EEEtoNumber(tmp)
        self.metadata.setMetadataPair(metadata.METADATA_SCENE_CENTER_LON, tmp)
        tmp1 = self.metadata.getMetadataValue(metadata.METADATA_SCENE_CENTER_LAT)
        tmp1=formatUtils.EEEtoNumber(tmp1)
        self.metadata.setMetadataPair(metadata.METADATA_SCENE_CENTER_LAT, tmp1)
        self.metadata.setMetadataPair(metadata.METADATA_SCENE_CENTER, "%s %s" % (tmp1,tmp))

        # set scene center time, from the only we have: start time
        tmp = "%sT%sZ" % (self.metadata.getMetadataValue(metadata.METADATA_START_DATE), self.metadata.getMetadataValue(metadata.METADATA_START_TIME))
        #self.metadata.setMetadataPair(metadata.METADATA_SCENE_CENTER, "%sZ" % tmp)
        self.metadata.setMetadataPair(metadata.METADATA_SCENE_CENTER_TIME, tmp)

        # set start stop time from scene center time
        #scene_center_date=datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S')
        #print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ sceneCenter=%s; %s" % (tmp,scene_center_date.strftime('%Y-%m-%dT%H:%M:%S'))
        #scene_start=scene_center_date - timedelta(seconds=4, milliseconds=512)
        #scene_end=scene_center_date + timedelta(seconds=4, milliseconds=512)
        #self.metadata.setMetadataPair(metadata.METADATA_START_DATE, scene_start.strftime('%Y-%m-%d'))
        #self.metadata.setMetadataPair(metadata.METADATA_START_TIME, scene_start.strftime('%H:%M:%S.%f'))
        #self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, scene_end.strftime('%Y-%m-%d'))
        #self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, scene_end.strftime('%H:%M:%S.%f'))

        # new:
        start=formatUtils.datePlusMsec(tmp, -4512)
        stop=formatUtils.datePlusMsec(tmp, 4512)
        toks=start.split('T')
        self.metadata.setMetadataPair(metadata.METADATA_START_DATE, toks[0])
        self.metadata.setMetadataPair(metadata.METADATA_START_TIME, toks[1][0:-1])
        toks=stop.split('T')
        self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, toks[0])
        self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, toks[1][0:-1])
        
        
        # 
        self.buildTypeCode()


    #
    #
    #
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
    # extract also the corresponding image ROW/COL 
    # prepare the browse report footprint block
    #
    def extractFootprint(self, helper, met):
        # get preview resolution
        try:
            imw, imh=imageUtil.get_image_size(self.preview_path)
            if self.debug!=0:
                print "  ############# preview image size: w=%s; h=%s" % (imw, imh)
        except:
            print "###################### ERROR getting preview image size"

        # get tiff resolution
        tmpNodes=[]
        helper.getNodeByPath(None, 'Raster_Dimensions', None, tmpNodes)
        if len(tmpNodes)==1:
            ncols = helper.getNodeText(helper.getFirstNodeByPath(tmpNodes[0], 'NCOLS', None))
            nrows = helper.getNodeText(helper.getFirstNodeByPath(tmpNodes[0], 'NROWS', None))
            print "  ############# tiff image size: w=%s; h=%s" % (ncols, nrows)
        else:
            print "###################### ERROR getting tiff image size"

        rcol=int(ncols)/imw
        rrow=int(nrows)/imh
        print "  ############# ratio tiff/preview: rcol=%s; rrow=%s" % (rcol, rrow)
        
        footprint=""
        rowCol=""
        nodes=[]
        #helper.setDebug(1)
        helper.getNodeByPath(None, 'Dataset_Frame', None, nodes)
        if len(nodes)==1:
            vertexList=helper.getNodeChildrenByName(nodes[0], 'Vertex')
            if len(vertexList)==0:
                raise Exception("can not find footprint vertex")

            n=0
            closePoint=""
            closeRowCol=""
            for node in vertexList:
                lon = helper.getNodeText(helper.getFirstNodeByPath(node, 'FRAME_LON', None))
                lat = helper.getNodeText(helper.getFirstNodeByPath(node, 'FRAME_LAT', None))
                row = helper.getNodeText(helper.getFirstNodeByPath(node, 'FRAME_ROW', None))
                col = helper.getNodeText(helper.getFirstNodeByPath(node, 'FRAME_COL', None))
                if self.debug!=0:
                    print "  ############# vertex %d: lon:%s  lat:%s" % (n, lon, lat)
                if len(footprint)>0:
                    footprint="%s " % (footprint)
                if len(rowCol)>0:
                    rowCol="%s " % (rowCol)
                footprint="%s%s %s" % (footprint, formatUtils.EEEtoNumber(lat), formatUtils.EEEtoNumber(lon))
                okRow=int(row)/rcol
                okCol=int(col)/rrow
                if row=='1':
                    okRow=1
                if col=='1':
                    okCol=1
                rowCol="%s%s %s" % (rowCol, okRow, okCol)
                
                if n==0:
                    closePoint = "%s %s" % (formatUtils.EEEtoNumber(lat), formatUtils.EEEtoNumber(lon))
                    closeRowCol = "%s %s" % (okRow, okCol)
                n=n+1
            footprint="%s %s" % (footprint, closePoint)
            rowCol="%s %s" % (rowCol, closeRowCol)

            # number of nodes in footprint
            met.setMetadataPair(browse_metadata.BROWSE_METADATA_FOOTPRINT_NUMBER_NODES, "%s" % (n+1))
                

            # make it CCW
            #met.setMetadataPair(metadata.METADATA_FOOTPRINT, formatUtils.reverseFootprint(footprint))
            met.setMetadataPair(metadata.METADATA_FOOTPRINT, footprint)
            met.setMetadataPair(metadata.METADATA_FOOTPRINT_IMAGE_ROWCOL, rowCol)
            
        return footprint, rowCol
        

    #
    #
    #
    def toString(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        return res


    #
    #
    #
    def dump(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        print res

