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
from browseImage import BrowseImage
import metadata
import browse_metadata
import formatUtils
from datetime import datetime, timedelta
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.insert(0,currentdir)
import imageUtil
from definitions_EoSip import sipBuilder

class Dimap_Spot_Product(Directory_Product):

    PREVIEW_NAME='preview.jpg'
    IMAGERY_NAME='imagery.tif'
    METADATA_NAME='metadata.dim'
    EXTRACTED_PATH=None
    preview_data=None
    metadata_data=None
    preview_path=None
    metadata_path=None
    imagery_path=None



    xmlMapping={metadata.METADATA_START_DATE:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE',
                metadata.METADATA_START_TIME:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME',
                metadata.METADATA_PARENT_IDENTIFIER:'Dataset_Sources/Source_Information/SOURCE_ID',
                metadata.METADATA_PROCESSING_TIME:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_PROCESSING_CENTER:'Production/Production_Facility/PROCESSING_CENTER',
                metadata.METADATA_SOFTWARE_NAME:'Production/Production_Facility/SOFTWARE_NAME',
                metadata.METADATA_SOFTWARE_VERSION:'Production/Production_Facility/SOFTWARE_VERSION',
                metadata.METADATA_DATASET_NAME:'Dataset_Id/DATASET_NAME',
                metadata.METADATA_ORBIT:'Dataset_Sources/Source_Information/Scene_Source/Imaging_Parameters/REVOLUTION_NUMBER',
                metadata.METADATA_PARENT_PRODUCT:'Dataset_Sources/Source_Information/SOURCE_ID',
                metadata.METADATA_PLATFORM:'Dataset_Sources/Source_Information/Scene_Source/MISSION',
                metadata.METADATA_PLATFORM_ID:'Dataset_Sources/Source_Information/Scene_Source/MISSION_INDEX',
                #metadata.METADATA_PROCESSING_LEVEL:'Dataset_Sources/Source_Information/Scene_Source/SCENE_PROCESSING_LEVEL',
                metadata.METADATA_INSTRUMENT:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_INSTRUMENT_ID:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX',
                metadata.METADATA_SENSOR_NAME:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_SENSOR_CODE:'Dataset_Sources/Source_Information/Scene_Source/SENSOR_CODE',
                metadata.METADATA_DATA_FILE_PATH:'Data_Access/Data_File/DATA_FILE_PATH@href',
                metadata.METADATA_DATASET_PRODUCTION_DATE:'Production/DATASET_PRODUCTION_DATE',
                
                #metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE',
                metadata.METADATA_INSTRUMENT_ALONG_TRACK_INCIDENCE_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE',
                
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
    # extract the source product in workfolder.
    # keep the metadata file content
    # dont_extract parameter can be used to not do the extract: to correct a faulty product then re package it in EoSip 
    #
    def extractToPath(self, folder=None, dont_extract=False):
        global METADATA_NAME,PREVIEW_NAME,IMAGERY_NAME
        if not os.path.exists(folder):
            raise Exception("destination folder does not exists:%s" % folder)
        if self.debug!=0:
            print " will exttact product to path:%s" % folder
        fh = open(self.path, 'rb')
        z = zipfile.ZipFile(fh)

        # keep list of content
        self.contentList=[]
        n=0
        d=0
        for name in z.namelist():
            n=n+1
            if self.debug!=0:
                print "  zip content[%d]:%s" % (n, name)
            if name.find(self.PREVIEW_NAME)>=0:
                self.preview_path="%s/%s" % (folder, name)
            elif name.find(self.METADATA_NAME)>=0:
                self.metadata_path="%s/%s" % (folder, name)
            elif name.find(self.IMAGERY_NAME)>=0:
                self.imagery_path="%s/%s" % (folder, name)
                
            if self.debug!=0:
                print "   %s extracted at path:%s" % (name, folder+'/'+name)
            if name.endswith('/'):
                d=d+1
            self.contentList.append(name)

        # ESA SPOT products only have one scene in one folder
        if d==1:
            if dont_extract!=True:
                z.extractall(folder)
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
        z.close()
        fh.close()



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
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV2_X__1P')
            else:
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRV#_#_##')
                self.processInfo.addInfo("STRANGE", "%s: sensorName:%s sensorName:%s" % (self.path, metadata.METADATA_SENSOR_NAME, self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)))
                        
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
                self.processInfo.addInfo("STRANGE", "%s: sensorName:%s sensorName:%s" % (self.path, metadata.METADATA_SENSOR_NAME, self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)))

        elif (self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='HRG'):
            if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='1' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='J':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG1_X__1P')
            elif self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID)=='2' and self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)=='J':
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG2_X__1P')
            else:
                self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'HRG#_#_##')
                self.processInfo.addInfo("STRANGE", "%s: sensorName:%s sensorName:%s" % (self.path, metadata.METADATA_SENSOR_NAME, self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)))

        else:
            self.processInfo.addInfo("STRANGE 2", "%s: sensorName:%s sensorName:%s" % (self.path, metadata.METADATA_SENSOR_NAME, self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE)))
            raise Exception("Product type UNKNOWN")
        
        self.processInfo.addInfo(metadata.METADATA_SENSOR_CODE, self.metadata.getMetadataValue(metadata.METADATA_SENSOR_CODE))
        self.processInfo.addInfo(metadata.METADATA_INSTRUMENT_ID, self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ID))
        self.processInfo.addInfo(metadata.METADATA_SENSOR_NAME, self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME))
        self.processInfo.addInfo(metadata.METADATA_TYPECODE, self.metadata.getMetadataValue(metadata.METADATA_TYPECODE))

       
    #
    #
    #
    def extractMetadata(self, met=None):
        #self.debug=1
        if met==None:
            raise Exception("metadate is None")

        
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

        # extract 'Dataset_Sources/Source_Information/Scene_Source/VIEWING_ANGLE' which is only in SPOT5, set it in acrossTrackIncidenceAngle 
        tmpNodes=[]
        helper.getNodeByPath(None, 'Dataset_Sources/Source_Information/Scene_Source/VIEWING_ANGLE', None, tmpNodes)
        if len(tmpNodes)==1:
            tmp=helper.getNodeText(tmpNodes[0])
            #print "  ############# VIEWING_ANGLE=%s" % viewingAngle
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT_ACROSS_TRACK_INCIDENCE_ANGLE, tmp)
        #else:
        #    print "###################### no VIEWING_ANGLE"
                            
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

        #tmp = self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE)
        #if tmp!=None:
        #    self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE, formatUtils.EEEtoNumber(tmp))

        tmp = self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ALONG_TRACK_INCIDENCE_ANGLE)
        if tmp!=sipBuilder.VALUE_NOT_PRESENT:
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT_ALONG_TRACK_INCIDENCE_ANGLE, formatUtils.EEEtoNumber(tmp))

        tmp = self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_ACROSS_TRACK_INCIDENCE_ANGLE)
        if tmp!=sipBuilder.VALUE_NOT_PRESENT:
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT_ACROSS_TRACK_INCIDENCE_ANGLE, formatUtils.EEEtoNumber(tmp))

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
        self.metadata.setMetadataPair(metadata.METADATA_SCENE_CENTER_TIME, tmp)
        # new:
        start=formatUtils.datePlusMsec(tmp, -4512)
        stop=formatUtils.datePlusMsec(tmp, 4512)
        toks=start.split('T')
        self.metadata.setMetadataPair(metadata.METADATA_START_DATE, toks[0])
        self.metadata.setMetadataPair(metadata.METADATA_START_TIME, toks[1][0:-1])
        toks=stop.split('T')
        self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, toks[0])
        self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, toks[1][0:-1])

        # verify that the WRS grid is ok: vs the scene id
        # BUT there is also this info in the parent identifier: Dataset_Sources/Source_Information/SOURCE_ID like: 10223228810091145361X
        # SPOT has GRS (K, J) pair. J is lat. K is long. also track/frame
        # <S><KKK><JJJ><YY><MM><DD><HH><MM><SS><I><M>: 21 cars
        #    S is the satellite number
        #    KKK and JJJ are the GRS designator of the scene (lon, lat)
        #    YY, MM, DD, HH, MM, SS are the date and time of the center of the scene 
        #    I is the instrument number
        #    M is the spectral mode of acquisition
        id = self.metadata.getMetadataValue(metadata.METADATA_PARENT_IDENTIFIER)
        print "@@@@@@@@@@@@@@@@@@@@@@@@@  id:%s" % id
        if id==None:
            raise Exception("no parent identifier:'%s'" % (id))
        if len(id)!=21:
            raise Exception("parent identifier is not 21 cars but %d:'%s'" % (len(id), id))

        tmp=self.metadata.getMetadataValue(metadata.METADATA_PLATFORM_ID)
        if id[0]!=tmp:
            raise Exception("parent identifier/METADATA_PLATFORM_ID missmatch:%s/'%s'" % (id[0],tmp))
            
        tmp = self.metadata.getMetadataValue(metadata.METADATA_WRS_LONGITUDE_GRID_NORMALISED)
        if id[1:4]!=tmp:
            raise Exception("parent identifier/METADATA_WRS_LONGITUDE_GRID_NORMALISED missmatch:%s/'%s'" % (id[1:4],tmp))

        tmp = self.metadata.getMetadataValue(metadata.METADATA_WRS_LATITUDE_GRID_NORMALISED)
        if id[4:7]!=tmp:
            raise Exception("parent identifier/METADATA_WRS_LATITUDE_GRID_NORMALISED missmatch:%s/'%s'" % (id[1:4],tmp))

        # check vs scene center time: 1988-10-09T11:45:36Z
        tmp = self.metadata.getMetadataValue(metadata.METADATA_SCENE_CENTER_TIME)
        if id[7:9]!=tmp[2:4]:
            raise Exception("parent identifier/METADATA_SCENE_CENTER_TIME YY missmatch:%s/'%s'" % (id[7:9],tmp[2:4]))
        if id[9:11]!=tmp[5:7]:
            raise Exception("parent identifier/METADATA_SCENE_CENTER_TIME MM missmatch:%s/'%s'" % (id[9:11],tmp[5:7]))
        if id[11:13]!=tmp[8:10]:
            raise Exception("parent identifier/METADATA_SCENE_CENTER_TIME DD missmatch:%s/'%s'" % (id[11:12],tmp[8:10]))
        if id[13:15]!=tmp[11:13]:
            raise Exception("parent identifier/METADATA_SCENE_CENTER_TIME HH missmatch:%s/'%s'" % (id[13:15],tmp[11:13]))
        if id[15:17]!=tmp[14:16]:
            raise Exception("parent identifier/METADATA_SCENE_CENTER_TIME MN missmatch:%s/'%s'" % (id[15:17],tmp[14:16]))
        if id[17:19]!=tmp[17:19]:
            raise Exception("parent identifier/METADATA_SCENE_CENTER_TIME SS missmatch:%s/'%s'" % (id[17:19],tmp[17:19]))
        # 
        self.buildTypeCode()


    #
    #
    #
    def extractQuality(self, helper, met):
        return 0


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
                

            # make sure the footprint is CCW
            # also prepare CW for EoliSa index and shopcart
            browseIm = BrowseImage()
            browseIm.setFootprint(footprint)
            browseIm.calculateBoondingBox()
            browseIm.setColRowList(rowCol)
            print "browseIm:%s" % browseIm.info()
            if not browseIm.getIsCCW():
                # keep for eolisa
                met.setMetadataPair(metadata.METADATA_FOOTPRINT_CW, browseIm.getFootprint())

                # and reverse
                print "############### reverse the footprint; before:%s; colRowList:%s" % (footprint,rowCol)
                browseIm.reverseFootprint()
                print "###############             after;%s; colRowList:%s" % (browseIm.getFootprint(), browseIm.getColRowList())
                met.setMetadataPair(metadata.METADATA_FOOTPRINT, browseIm.getFootprint())
                met.setMetadataPair(metadata.METADATA_FOOTPRINT_IMAGE_ROWCOL, browseIm.getColRowList())
            else:
                met.setMetadataPair(metadata.METADATA_FOOTPRINT, footprint)
                met.setMetadataPair(metadata.METADATA_FOOTPRINT_IMAGE_ROWCOL, rowCol)

                #reverse for eolisa
                met.setMetadataPair(metadata.METADATA_FOOTPRINT_CW, browseIm.reverseSomeFootprint(footprint))
                
            # boundingBox is needed in the localAttributes
            met.setMetadataPair(metadata.METADATA_BOUNDING_BOX, browseIm.boondingBox)
            closedBoundingBox = "%s %s %s" % (browseIm.boondingBox, browseIm.boondingBox.split(" ")[0], browseIm.boondingBox.split(" ")[1])
            met.setMetadataPair(metadata.METADATA_BOUNDING_BOX_CW_CLOSED, browseIm.reverseSomeFootprint(closedBoundingBox))
            met.addLocalAttribute("boundingBox", met.getMetadataValue(metadata.METADATA_BOUNDING_BOX))

            
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

