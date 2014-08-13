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
from definitions_EoSip import sipBuilder
from browseImage import BrowseImage
import metadata
import browse_metadata
import formatUtils
import geomHelper

class Dimap_Tropforest_Product(Directory_Product):

    TIF_FILE_SUFFIX='.tif'
    XML_FILE_SUFFIX='.XML'
    TIF_FILE_NAME=None
    XML_FILE_NAME=None
    EXTRACTED_PATH=None

    xmlMapping={metadata.METADATA_START_DATE:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE',
                metadata.METADATA_START_TIME:'Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME',
                metadata.METADATA_PROCESSING_TIME:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_PROCESSING_CENTER:'Production/DATASET_PRODUCER_NAME',
                metadata.METADATA_DATASET_NAME:'Dataset_Id/DATASET_NAME',
                metadata.METADATA_PLATFORM:'Dataset_Sources/Source_Information/Scene_Source/MISSION',
                metadata.METADATA_PLATFORM_ID:'Dataset_Sources/Source_Information/Scene_Source/MISSION_INDEX',
                metadata.METADATA_INSTRUMENT:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_INSTRUMENT_ID:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX',
                metadata.METADATA_SENSOR_NAME:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT',
                metadata.METADATA_SENSOR_CODE:'Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT_INDEX',
                metadata.METADATA_DATA_FILE_PATH:'Data_Access/Data_File/DATA_FILE_PATH@href',
                metadata.METADATA_DATASET_PRODUCTION_DATE:'Production/DATASET_PRODUCTION_DATE',
                metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE',
                metadata.METADATA_VIEWING_ANGLE:'Dataset_Sources/Source_Information/Scene_Source/VIEWING_ANGLE',
                metadata.METADATA_SUN_AZIMUTH:'Dataset_Sources/Source_Information/Scene_Source/SUN_AZIMUTH',
                metadata.METADATA_SUN_ELEVATION:'Dataset_Sources/Source_Information/Scene_Source/SUN_ELEVATION',
                metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER:'Coordinate_Reference_System/Horizontal_CS/HORIZONTAL_CS_CODE',
                metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER_NAME:'Coordinate_Reference_System/Horizontal_CS/HORIZONTAL_CS_NAME'
                }

    def __init__(self, path=None):
        Directory_Product.__init__(self, path)
        print " init class Dimap_Tropforest_Product"

    #
    # 
    #
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


    #
    # extract the tropforest product
    # keep the metadata+browse file path
    # Note that Deimos metadata in .met file are more conplet
    #
    def extractToPath(self, folder=None):
        if not os.path.exists(folder):
            raise Exception("destination fodler does not exists:%s" % folder)
        if self.debug!=0:
            print " will exttact product to path:%s" % folder
        fh = open(self.path, 'rb')
        z = zipfile.ZipFile(fh)

        # keep list of content
        self.contentList=[]
        # 
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
                # test if Deimos product: DE1 in filename
                if name.find("DE1")>0:
                    self.XML_FILE_NAME=name.replace(self.XML_FILE_SUFFIX, ".met")
                else:
                    self.XML_FILE_NAME=name
            if self.debug!=0:
                print "   %s extracted at path:%s" % (name, folder+'/'+name)
            self.contentList.append(name)
        fh.close()
        self.EXTRACTED_PATH=folder


    #
    # extract the grid from filaname: N00-E113_AVN_20090517_PRO_0.tif or N00_W055_DE1_20101109_PRO_0.tif
    # return a string 
    #
    def extractGridFromFile(self,value):
        if value==None:
            raise Exception("value (lat/lon) is None")
        pos=self.TIF_FILE_NAME.find('-')
        if pos>0:
            grid=self.TIF_FILE_NAME.split('_')[0]
            if value=="lat":
                grid_final=grid.split('-')[0]
                if grid_final[0]=="N":
                    grid_final=grid_final[1:]
                elif grid_final[0]=="S":
                    grid_final="-%s" % grid_final[1:]
                else:
                    raise Exception("lat is malformed if filename:%s" % self.TIF_FILE_NAME)
            elif value=="lon":
                grid_final=grid.split('-')[1]
                if grid_final[0]=="E":
                    grid_final=grid_final[1:]
                elif grid_final[0]=="W":
                    grid_final="-%s" % grid_final[1:]
                else:
                    raise Exception("lon is malformed if filename:%s" % self.TIF_FILE_NAME)
        else:
            grid=self.TIF_FILE_NAME.split('_')
            if value=="lat":
                grid_final=grid[0]
                if grid_final[0]=="N":
                    grid_final=grid_final[1:]
                elif grid_final[0]=="S":
                    grid_final="-%s" % grid_final[1:]
                else:
                    raise Exception("lat is malformed if filename:%s" % self.TIF_FILE_NAME)
            elif value=="lon":
                grid_final=grid[1]
                if grid_final[0]=="E":
                    grid_final=grid_final[1:]
                elif grid_final[0]=="W":
                    grid_final="-%s" % grid_final[1:]
                else:
                    raise Exception("lon is malformed if filename:%s" % self.TIF_FILE_NAME)
        return grid_final


    #
    # normalise the grid to 4 digit
    #
    def extractGridFromFileNormalised(self, value):
        if value==None:
            raise Exception("value (lat/lon) is None")
        grid_final=self.extractGridFromFile(value)
        if value=="lat":
            grid_final="%s" % formatUtils.coLatitude(int(grid_final))
        elif value=="lon":
            grid_final="%s" % formatUtils.absoluteLongitude(int(grid_final))
            
        grid_final=grid_final.rjust(3,"0")
        return grid_final


    #
    #
    #
    def buildTypeCode(self):
        if self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='AVNIR':
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'AV2_OBS_2F')
        elif self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)=='SLIM-6-22':
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'SL6_L1T_2F') # or SL6_L1R_1P
        elif self.metadata.getMetadataValue(metadata.METADATA_SENSOR_NAME)==None:  # KOMPSAT
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'MSC_MS__2F ') 
        else:
            self.metadata.setMetadataPair(metadata.METADATA_TYPECODE,'###_###_##')


    #
    #
    #
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

        # keep the original product name, add it to local attributes
        #met.addLocalAttribute("original_name", met.getMetadataValue(metadata.METADATA_DATASET_NAME))
        #met.addLocalAttribute("original_name", self.origName)

                            
        return num_added


    #
    # refine the metada, should perform in order:
    # - normalise date and time
    # - set platform info
    # - build type code
    #
    def refineMetadata(self):
        # test that footprint is valid (not almost a point)
        tmp=self.metadata.getMetadataValue(metadata.METADATA_FOOTPRINT)
        toks=tmp.split(" ")
        dist=geomHelper.metersDistanceBetween(float(toks[0]), float(toks[1]), float(toks[2]), float(toks[3]))
        if dist < 1000: # in meters
            raise Exception("footprint is too small:%s" % dist)
        #print "DISTANCE=%s" % dist
        
        # set platform Id and instrument. Overwrite readed values
        if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM)=='ALOS':
            #if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM_ID)==None:
            self.metadata.setMetadataPair(metadata.METADATA_PLATFORM_ID, '1')
            #if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT)==None:
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT, 'AVNIR-2')
        elif self.metadata.getMetadataValue(metadata.METADATA_PLATFORM)=='KOMPSAT':
            #if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT)==None:
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT, 'MSC')
            #if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM_ID)==None:
            self.metadata.setMetadataPair(metadata.METADATA_PLATFORM_ID, '2')
        elif self.metadata.getMetadataValue(metadata.METADATA_PLATFORM)=='DEIMOS':
            #if self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT)==None:
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT, 'SLIM6')
            #if self.metadata.getMetadataValue(metadata.METADATA_PLATFORM_ID)==None:
            self.metadata.setMetadataPair(metadata.METADATA_PLATFORM_ID, '1')

        # add time 00:00:00 to processing time if needed
        tmp = self.metadata.getMetadataValue(metadata.METADATA_PROCESSING_TIME)
        if len(tmp) == 10:
            self.metadata.setMetadataPair(metadata.METADATA_PROCESSING_TIME, "%sT00:00:00Z" % tmp)

        # some product have empty start time
        if self.metadata.getMetadataValue(metadata.METADATA_START_TIME)==None:
            self.metadata.setMetadataPair(metadata.METADATA_START_TIME, "00:00:00")
        if self.metadata.getMetadataValue(metadata.METADATA_STOP_TIME)==None:
            self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, "00:00:00")

        # set orbit to 000000 if None
        if self.metadata.getMetadataValue(metadata.METADATA_ORBIT)==None:
            self.metadata.setMetadataPair(metadata.METADATA_ORBIT, "000000")

        # suppress 'L' charactere in metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE
        tmp = self.metadata.getMetadataValue(metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE)
        if tmp != None and tmp[0]=='L':
            tmp = tmp[1:]
            self.metadata.setMetadataPair(metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE, tmp)
            
        # 
        self.buildTypeCode() 

    #
    # extract quality for deimos
    #
    def extractDeimosQuality(self, helper, met):
        tmp = self.EXTRACTED_PATH+'/'+self.XML_FILE_NAME
        tmp = tmp.replace('.met', '.XML')
        if self.debug!=0:
        	print "############@@@@@@@@@@@@@@@@@ deimos .XML file=%s" % tmp
        fd=open(tmp, 'r')
        data=fd.read()
        fd.close()

        helper=xmlHelper.XmlHelper()
        helper.setData(data);
        helper.parseData()
        
        #helper.setDebug(1)
        quality=[]
        helper.getNodeByPath(None, 'Quality_Assesment/Quality_Parameter/QUALITY_PARAMETER_DESC', None, quality)
        index=-1
        if self.debug!=0:
        	print "############@@@@@@@@@@@@@@@@@ 0 quality=%d" % len(quality)
        n=0
        for item in quality:
            if self.debug!=0:
            	    print "############@@@@@@@@@@@@@@@@@ quality[%d]=%s" % (n, helper.getNodeText(item))
            if helper.getNodeText(item)=='QC2 - % Clouds':
                index=n
            n=n+1
        #print "############@@@@@@@@@@@@@@@@@ want quality value at index:%d" % index

        
        quality=[]
        qualityValue=None
        helper.getNodeByPath(None, 'Quality_Assesment/Quality_Parameter/QUALITY_PARAMETER_VALUE', None, quality)
        if self.debug!=0:
        	print "############@@@@@@@@@@@@@@@@@ 1 quality=%d" % len(quality)
        n=0;
        for item in quality:
            if self.debug!=0:
            	    print "############@@@@@@@@@@@@@@@@@ quality[%d]=%s" % (n, helper.getNodeText(item))
            if index==n:
                qualityValue=helper.getNodeText(item)
            n=n+1
        #print "############@@@@@@@@@@@@@@@@@ cloud qualityValue=%s" % (qualityValue)
        met.setMetadataPair(metadata.METADATA_CLOUD_COVERAGE, qualityValue)
        return 1 
        
    #
    # extract quality for kompsat and avnir
    #
    def extractQuality(self, helper, met):
        # for deimos we use the .met xml. but the cloud cover is only in the .xml. 
        if met.getMetadataValue(metadata.METADATA_PLATFORM)=='DEIMOS':
            self.extractDeimosQuality(helper, met)
            return 1
        
        #helper.setDebug(1)
        quality=[]
        helper.getNodeByPath(None, 'Quality_Assesment/Quality_Parameter/QUALITY_PARAMETER_DESC', None, quality)
        index=-1
        if self.debug!=0:
        	print "############@@@@@@@@@@@@@@@@@ 0 quality=%d" % len(quality)
        n=0
        for item in quality:
            if self.debug!=0:
            	    print "############@@@@@@@@@@@@@@@@@ quality[%d]=%s" % (n, helper.getNodeText(item))
            if helper.getNodeText(item)=='QC2 - % Clouds':
                index=n
            n=n+1
        #print "############@@@@@@@@@@@@@@@@@ want quality value at index:%d" % index

        
        quality=[]
        qualityValue=None
        helper.getNodeByPath(None, 'Quality_Assesment/Quality_Parameter/QUALITY_PARAMETER_VALUE', None, quality)
        if self.debug!=0:
        	print "############@@@@@@@@@@@@@@@@@ 1 quality=%d" % len(quality)
        n=0;
        for item in quality:
            if self.debug!=0:
            	    print "############@@@@@@@@@@@@@@@@@ quality[%d]=%s" % (n, helper.getNodeText(item))
            if index==n:
                qualityValue=helper.getNodeText(item)
            n=n+1
        #print "############@@@@@@@@@@@@@@@@@ cloud qualityValue=%s" % (qualityValue)
        met.setMetadataPair(metadata.METADATA_CLOUD_COVERAGE, qualityValue)
        return 1


    #
    # extract the footprint posList point, ccw, lat lon
    # NOTE: Deimos products have UTM coordinates in meters
    # prepare the browse report footprint block
    #
    def extractFootprint(self, helper, met):
        nodes=[]
        helper.getNodeByPath(None, 'Geoposition/Geoposition_Insert', None, nodes)
        if len(nodes)==1:
            footprint=None
            rowCol=None
            ulx = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'ULXMAP', None))
            uly = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'ULYMAP', None))
            try: # next for non Deimos products
                brx = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'BRXMAP', None))
                bry = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'BRYMAP', None))
                if self.debug!=0:
                    print " ulx:%s  uly:%s  brx:%s  bry:%s" % (ulx, uly, brx, bry)
                # store it for browse report in rectified browse
                # should be in lower left lat/lon + upper right lat/lon.
                met.setMetadataPair(browse_metadata.BROWSE_METADATA_RECT_COORDLIST, "%s %s %s %s" % (bry, ulx, uly , brx))

                # make the product metadata report footprint in ccw order
                footprint="%s %s %s %s %s %s %s %s %s %s" % (uly, ulx,   bry, ulx,   bry, brx,   uly, brx,   uly, ulx)
                if self.debug!=0:
                    print " posList:%s" % footprint
                met.setMetadataPair(metadata.METADATA_FOOTPRINT, footprint)
            except:
                #self.debug=1
                # for Deimos products
                #helper.setDebug(1)
                # get the UTM zone and number
                # is like: WGS 84 / UTM zone 21N
                # ==>extract 21 and N
                footprint=''
                utmInfo=met.getMetadataValue(metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER_NAME)
                lastTok=utmInfo.split(" ")[-1]
                zone=lastTok[-1]
                zoneNumber=lastTok[0:-1]
                if self.debug!=0:
                    print " ################# utm info:'%s'; zone:'%s'; zone number:'%s'" % (utmInfo, zone, zoneNumber)
                nodes2=[]
                helper.getNodeByPath(None, 'Dataset_Frame/Vertex', None, nodes2)
                #
                # keep first + 2th and 4th point to close the polygon and make the rectBrose BL/UR corners
                #
                if len(nodes2)!=0:
                    n=0
                    for vertex in nodes2:
                        x_m=helper.getNodeText(helper.getFirstNodeByPath(vertex, 'FRAME_X', None))
                        y_m=helper.getNodeText(helper.getFirstNodeByPath(vertex, 'FRAME_Y', None))
                        if self.debug!=0:
                            print " ################# coords in UTM:%s; %s" % (x_m, y_m)
                        lat,lon=formatUtils.utmToLatLon(float(x_m), float(y_m), int(zoneNumber), zone)
                        if self.debug!=0:
                            print " ################# coords in lat lon: lat=%s; lon=%s" % (lat, lon)
                        if n==0:
                            first_lat=lat
                            first_lon=lon
                        if n==1:
                            second_lat=lat
                            second_lon=lon
                        if n==3:
                            fourth_lat=lat
                            fourth_lon=lon
                        if len(footprint)>0:
                            footprint="%s " % footprint
                        footprint="%s%s %s" % (footprint, lat, lon)
                        n=n+1
                    footprint="%s %s %s" % (footprint, first_lat, first_lon)
                    if self.debug!=0:
                        print " ################# footprint:%s" % footprint
                    #
                    # deimos are already in CCW order. it seems
                    #
                    #met.setMetadataPair(metadata.METADATA_FOOTPRINT, formatUtils.reverseFootprint(footprint))
                    met.setMetadataPair(metadata.METADATA_FOOTPRINT, footprint)

                    # store it for browse report in rectified browse
                    # should be in lower left lat/lon + upper right lat/lon.
                    met.setMetadataPair(browse_metadata.BROWSE_METADATA_RECT_COORDLIST, "%s %s %s %s" % (second_lat, second_lon, fourth_lat , fourth_lon))
                else:
                    print " ERROR: Dataset_Frame/Vertex not found:%d" % len(nodes2)
                    raise Exception(" ERROR: Dataset_Frame/Vertex not found:%d" % len(nodes2))


            # extract also COUNTRY, add it to local attributes
            # Deimos doesn't have this info
            if met.getMetadataValue(metadata.METADATA_PLATFORM)!='DEIMOS':
                #print "@@@@@@@@@@@@@ nodes=%s" % nodes
                #print "@@@@@@@@@@@@@ nodes[0]=%s" % nodes[0]
                #helper.setDebug(1)
                country = helper.getNodeText(helper.getFirstNodeByPath(nodes[0], 'COUNTRY', None))
                met.setMetadataPair(metadata.METADATA_COUNTRY, country)
                met.addLocalAttribute("observedCountry", country)


            # make sure the footprint is CCW
            browseIm = BrowseImage()
            browseIm.setFootprint(footprint)
            browseIm.calculateBoondingBox()
            browseIm.setColRowList(rowCol)
            print "browseIm:%s" % browseIm.info()
            if not browseIm.getIsCCW():
                print "############### reverse the footprint; before:%s; colRowList:%s" % (footprint,rowCol)
                browseIm.reverseFootprint()
                print "###############             after;%s; colRowList:%s" % (browseIm.getFootprint(), browseIm.getColRowList())
                met.setMetadataPair(metadata.METADATA_FOOTPRINT, browseIm.getFootprint())
                met.setMetadataPair(metadata.METADATA_FOOTPRINT_IMAGE_ROWCOL, browseIm.getColRowList())
            else:
                met.setMetadataPair(metadata.METADATA_FOOTPRINT, footprint)
                met.setMetadataPair(metadata.METADATA_FOOTPRINT_IMAGE_ROWCOL, rowCol)
                pass
            # calculate center if not already set
            centerPair = met.getMetadataValue(metadata.METADATA_SCENE_CENTER)
            if centerPair==sipBuilder.VALUE_NOT_PRESENT:
                lat, lon = browseIm.calculateCenter()
                met.setMetadataPair(metadata.METADATA_SCENE_CENTER, "%s %s" % (lat, lon))
                met.setMetadataPair(metadata.METADATA_SCENE_CENTER_LAT, lat)
                met.setMetadataPair(metadata.METADATA_SCENE_CENTER_LON, lon)
            else:
                print "@@@@@@@@@@@@@@@#######################@@@@@@@@@@@@@@@@@@@@@ centerPair:%s" % centerPair
            # boundingBox is needed in the localAttributes
            met.setMetadataPair(metadata.METADATA_BOUNDING_BOX, browseIm.boondingBox)
            met.addLocalAttribute("boundingBox", met.getMetadataValue(metadata.METADATA_BOUNDING_BOX))


        else:
            print " ERROR: Geoposition/Geoposition_Insert has not 1 subnode but:%d" % len(nodes)
            raise Exception(" ERROR: Geoposition/Geoposition_Insert has not 1 subnode but:%d" % len(nodes))
        return
        

    def toString(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        return res


    def dump(self):
        res="tif file:%s" % self.TIF_FILE_NAME
        res="%s\nxml file:%s" % (res, self.XML_FILE_NAME)
        print res


