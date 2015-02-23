# -*- coding: cp1252 -*-
#
# this class represent a aeolus aux product. Single file
#
#
#
import os,sys,sys,inspect
import logging
import zipfile
import xmlHelper
from product import Product
from aeolus_product import Aeolus_Product
from directory_product import Directory_Product
from browseImage import BrowseImage
import metadata
import browse_metadata
import formatUtils
from datetime import datetime, timedelta
from definitions_EoSip import sipBuilder
from namingConvention_aeolus import NamingConvention_Aeolus
import shutil

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# import parent
parentdir = os.path.dirname(currentdir)
print "##### eoSip converter dir:%s" % parentdir
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)
import fileHelper



class Aeolus_Aux_Product(Aeolus_Product):

    METADATA_NAME='.EEF'
    EXTRACTED_PATH=None
    metadata_data=None
    metadata_path=None
    imagery_path=None



    xmlMapping={metadata.METADATA_START_DATE:'Earth_Explorer_Header/Variable_Header/Main_Product_Header/Sensing_Start',
                metadata.METADATA_STOP_DATE:'Earth_Explorer_Header/Variable_Header/Main_Product_Header/Sensing_Stop',

                metadata.METADATA_TYPECODE:'Earth_Explorer_Header/Fixed_Header/File_Type',
                metadata.METADATA_FILECLASS:'Earth_Explorer_Header/Fixed_Header/File_Class',
                metadata.METADATA_PRODUCT_VERSION:'Earth_Explorer_Header/Fixed_Header/Baseline',
                #metadata.METADATA_PRODUCT_VERSION:'Fixed_Header/File_Version',
                #metadata.METADATA_PROCESSING_TIME:'Fixed_Header/Source/Creation_Date',
                metadata.METADATA_PROCESSING_TIME:'Earth_Explorer_Header/Variable_Header/Main_Product_Header/Proc_Time',
                metadata.METADATA_PROCESSING_CENTER:'Earth_Explorer_Header/Fixed_Header/Source/System',
                metadata.METADATA_SOFTWARE_NAME:'Earth_Explorer_Header/Fixed_Header/Source/Creator',
                metadata.METADATA_SOFTWARE_VERSION:'Earth_Explorer_Header/Fixed_Header/Source/Creator_Version',
                #metadata.METADATA_ACQUISITION_CENTER:'Variable_Header/Main_Product_Header/Acquisition_Station',
                metadata.METADATA_DATASET_NAME:'Earth_Explorer_Header/Variable_Header/Main_Product_Header/Product',
                
                metadata.METADATA_ORBIT:'Earth_Explorer_Header/Variable_Header/Main_Product_Header/Abs_Orbit',
                metadata.METADATA_TRACK:'Earth_Explorer_Header/Variable_Header/Main_Product_Header/Rel_Orbit',
                metadata.METADATA_PLATFORM:'Earth_Explorer_Header/Fixed_Header/Mission',


                # various and specific parameters:
                # TODO: clean this + ADV_ORDER, define constants
                'VARIOUS_HEADER_SYSTEM':'Earth_Explorer_Header/Fixed_Header/Source/System',
                'ADV_minRollAngle':'__FIXED:0.0',
                'ADV_maxRollAngle':'__FIXED:0.0',
                'ADV_minPitchAngle':'__FIXED:0.0',
                'ADV_maxPitchAngle':'__FIXED:0.0',
                'ADV_minYawAngle':'__FIXED:0.0',
                'ADV_maxYawAngle':'__FIXED:0.0'
                }

    ADV_ORDER=['ADV_minRollAngle', 'ADV_maxRollAngle', 'ADV_minPitchAngle', 'ADV_maxPitchAngle', 'ADV_minYawAngle', 'ADV_maxYawAngle']
    
    #
    # create source product:
    # - a .EE file
    # - None
    #
    def __init__(self, path, otherPath=None):
        Aeolus_Product.__init__(self, path, otherPath) # otherPath is None
        self.debug=1
        print " init class Aeolus_Aux_Product: path=%s" % (self.path)
        

    #
    #
    #
    def getMetadataInfo(self):
        return self.metadata_data


    #
    # source product is a single .EEF file
    #
    # keep the metadata file content
    # dont_extract parameter can be used to not do the extract: to correct a faulty product then re package it in EoSip 
    #
    def extractToPath(self, folder=None, dont_extract=False):
        global METADATA_NAME
        if not os.path.exists(folder):
            raise Exception("destination folder does not exists:%s" % folder)
        if self.debug!=0:
            print " will exttact product to path:%s" % folder

        print "   Aeolus_Aux_Product: path:%s" % (self.path)
        self.contentList=[]
        aFileHelper = fileHelper.fileHelper()
        self.metadata_path="%s/%s" % (folder, aFileHelper.basename(self.path))
        shutil.copyfile(self.path, self.metadata_path)
        print "Copied %s as %s" % (self.path, self.metadata_path)
        
        self.contentList.append(aFileHelper.basename(self.path))
        self.EXTRACTED_PATH=folder

        # get matadata xml
        fd=open(self.metadata_path, 'r')
        self.metadata_data=fd.read()
        fd.close()


       
    #
    #
    #
    def extractMetadata(self, met=None):
        #self.debug=1
        if met==None:
            raise Exception("metadate is None")

        
        # use what contains the metadata file
        metContent=self.getMetadataInfo()
        #print "################## metadata:%s" % metContent
        
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
            if self.xmlMapping[field] != '':
                if self.xmlMapping[field].find("@")>=0:
                    attr=self.xmlMapping[field].split('@')[1]
                    path=self.xmlMapping[field].split('@')[0]
                else:
                    attr=None
                    path=self.xmlMapping[field]

                if self.debug!=0:
                    print "  look metadata at xml path:%s" % (path)
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

        return num_added


    #
    # refine the metada, should perform in order:
    # - normalise date and time
    # - set platform info
    # - build type code
    #
    def refineMetadata(self):
        # do some check on product:
        # set configured naming convention
        namingConventionEo = NamingConvention_Aeolus(self.OUTPUT_EO_PATTERN)

        # find matching instance pattern
        namingPattern = namingConventionEo.guessPatternUsed(self.origName, namingConventionEo.possible_pattern )
        if len(namingPattern)==1:
            print "aeolus instance pattern is:%s" % namingPattern[0]
            namingConventionEo.usePatternvalue(namingPattern[0])
        else:
            raise  Exception("can not find aeolus instance pattern for filename:%s" % self.origName)
        
        # get product type
        ptype=namingConventionEo.getFilenameElement(self.origName, NamingConvention_Aeolus.EOLUS_PATTERN, 'TTTTTTTTTT')
        print "typecode from pattern:%s" % ptype
        if ptype[-2]=='2':
            print " ################################################################## change eo naming convention to NamingConvention_Aeolus.EOLUS_PATTERN_INSTANCE_GENERIC_DDV"
            namingConventionEo = NamingConvention_Aeolus(NamingConvention_Aeolus.EOLUS_PATTERN_INSTANCE_GENERIC_DDV)

        
        # verigy that filename has expected length
        originalFileName = self.metadata.getMetadataValue(metadata.METADATA_ORIGINAL_NAME)
        originalShortName=originalFileName.split('.')[0]
        if not namingConventionEo.isFileLengthOk(originalShortName):
            raise Exception("incorrect file length:%s" % (originalShortName))

        # extract start time msec:
        # TODO: add this possibility in naming convention, passing the pattern-element as argument
        dateTime=originalShortName[19:37]
        #dateTime=namingConventionEo.getFilenameElement(self.origName, NamingConvention_Aeolus.EOLUS_PATTERN, 'yyyymmddThhmmsszzz')
        #duration=originalShortName[38:47]
        if namingPattern[0]==NamingConvention_Aeolus.EOLUS_PATTERN_INSTANCE_GENERIC_DTOV:
            #duration=namingConventionEo.getFilenameElement(self.origName, NamingConvention_Aeolus.EOLUS_PATTERN, 'TTTTTTTTTT')
            duration=originalShortName[38:47]
            self.metadata.setMetadataPair(metadata.METADATA_START_TIME_MSEC, dateTime[-3:])
            self.metadata.setMetadataPair(metadata.METADATA_DURATION, duration)
        elif namingPattern[0]==NamingConvention_Aeolus.EOLUS_PATTERN_INSTANCE_GENERIC_DDV:
            self.metadata.setMetadataPair(metadata.METADATA_START_TIME_MSEC, dateTime[-3:])
            #dateTime=namingConventionEo.getFilenameElement(self.origName, NamingConvention_Aeolus.EOLUS_PATTERN, 'YYYYMMDDTHHMMSS')
        
        
        # start date time from: UTC=2010-10-02T00:00:00 stored in DATA + TIME + DATETIME
        tmp = self.metadata.getMetadataValue(metadata.METADATA_START_DATE).replace('UTC=', '')
        pos = tmp.find('T')
        date=None
        time=None
        if pos > 0:
            date=tmp[0:pos]
            time=tmp[pos+1:]
            # just 2 decimal after second
            pos2 = time.find('.')
            if pos2>0:
                time = time[0:(pos2+3)]
            self.metadata.setMetadataPair(metadata.METADATA_START_DATE, date)
            self.metadata.setMetadataPair(metadata.METADATA_START_TIME, time)
            
        else:
            raise Exception("invalid start date:"+tmp)

        # get the file version from filename
        #self.metadata.setMetadataPair(metadata.METADATA_SIP_VERSION, originalShortName[55:59])

        # idem stop time
        tmp = self.metadata.getMetadataValue(metadata.METADATA_STOP_DATE).replace('UTC=', '')
        pos = tmp.find("T")
        date=None
        time=None
        if pos > 0:
            date=tmp[0:pos]
            time=tmp[pos+1:]
            # just 2 decimal after second
            pos2 = time.find('.')
            if pos2>0:
                time = time[0:(pos2+3)]
            self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, date)
            self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, time)
        else:
            raise Exception("invalid stop date:"+tmp)

        # idem processing time
        tmp = self.metadata.getMetadataValue(metadata.METADATA_PROCESSING_TIME).replace('UTC=', '')
        pos = tmp.find("T")
        date=None
        time=None
        if pos > 0:
            date=tmp[0:pos]
            time=tmp[pos+1:]
            # just 2 decimal after second
            pos2 = time.find('.')
            if pos2>0:
                time = time[0:(pos2+3)]
            self.metadata.setMetadataPair(metadata.METADATA_PROCESSING_TIME, "%sT%sZ" % (date, time))
        else:
            raise Exception("invalid processing time:"+tmp)

        # time position == stop date + time
        self.metadata.setMetadataPair(metadata.METADATA_TIME_POSITION, "%sT%sZ" % (self.metadata.getMetadataValue(metadata.METADATA_STOP_DATE),self.metadata.getMetadataValue(metadata.METADATA_STOP_TIME)))

        # METADATA_WRS_LONGITUDE_GRID_NORMALISED
        #self.metadata.setMetadataPair(metadata.METADATA_WRS_LONGITUDE_GRID_NORMALISED, self.metadata.getMetadataValue(metadata.METADATA_TRACK))

        # suppress spaces arround ' / ' in the software name
        self.metadata.setMetadataPair(metadata.METADATA_SOFTWARE_NAME, self.metadata.getMetadataValue(metadata.METADATA_SOFTWARE_NAME).replace(' ', ''))
        
        # set acquisitionType
        OTHER=['ALD_U_N_0_', 'ALD_U_N_1A'] # OTHER
        NOMINAL=['ALD_U_N_1B', 'ALD_U_N_2A', 'ALD_U_N_2B', 'ALD_U_N_2C'] # NOMINAL
        CALIBRATION=['AUX_CAL_L2','AUX_CSR_1B','AUX_DCC_1A','AUX_DCC_1B','AUX_DCMZ1B','AUX_DMCZ1A','AUX_HBE_1B','AUX_IAT_1A','AUX_IAT_1B','AUX_IDC_1A','AUX_IDC_1B','AUX_IRC_1A','AUX_ISR_1A','AUX_ISR_1B','AUX_LCP_1A','AUX_LCP_1B','AUX_LDT_1A','AUX_LDT_1B','AUX_MRC_1B','AUX_NOU_1A','AUX_OWV_1A','AUX_OWV_1B','AUX_PRR_1B','AUX_RBC_L2','AUX_RRC_1B','AUX_ZWC_1B','AUX_RDB_1B']# CALIBRATION
        tmp = self.metadata.getMetadataValue(metadata.METADATA_TYPECODE)
        acqType='UNKNOWN'
        try:
                 index = OTHER.index(tmp)
                 acqType='OTHER'
        except:
                 try:
                     index = NOMINAL.index(tmp)
                     acqType='NOMINAL'
                 except:
                     try:
                         index = CALIBRATION.index(tmp)
                         acqType='CALIBRATION'
                     except:
                         acqType='UNKNOWN:%s not in LUT' % tmp
        self.metadata.setMetadataPair(metadata.METADATA_ACQUISITION_TYPE, acqType)

        # set processing level from last 2 digit of typecode
        pLevel=tmp[-2:]
        print "###################################################################### processing level:%s" %  pLevel
        if pLevel[0]=='2':
            pLevel='2'
        print "###################################################################### processing level after:%s" %  pLevel
        self.metadata.setMetadataPair(metadata.METADATA_PROCESSING_LEVEL, pLevel)


        # set product version to 1B01 if not present
        tmp=self.metadata.getMetadataValue(metadata.METADATA_PRODUCT_VERSION)
        if tmp!=sipBuilder.VALUE_NOT_PRESENT:
            self.metadata.setMetadataPair(metadata.METADATA_PRODUCT_VERSION, '1B01')


        # set sensor mode
        self.extractSensorMode()
        
        
        # set FILE classe:
        tmp = self.metadata.getMetadataValue(metadata.METADATA_FILECLASS)[0] + self.metadata.getMetadataValue('VARIOUS_HEADER_SYSTEM')[0:3]
        self.metadata.setMetadataPair(metadata.METADATA_FILECLASS, tmp)

        # handle specific information
        FIXED='__FIXED:'
        unorderedAdvDict={}
        for field in self.xmlMapping:
            if field[0:4]=='ADV_':
                mapping = self.xmlMapping[field]
                if mapping.startswith(FIXED):
                    print " ################################################################## handle ADV FIXED info: %s=%s" % (field, mapping)
                    fixedValue=mapping[len(FIXED):]
                    #self.metadata.addLocalAttribute(field[4:], fixedValue)
                    unorderedAdvDict[field[4:]]= fixedValue
                else:
                    tmp = self.metadata.getMetadataValue(field)
                    print " ################################################################## handle ADV info: %s=%s" % (field,tmp)
                    if tmp==None:
                        tmp="N/A"
                    #self.metadata.addLocalAttribute(field[4:], tmp)
                    unorderedAdvDict[field[4:]]= tmp

        for field in self.ADV_ORDER:
            self.metadata.addLocalAttribute(field[4:], unorderedAdvDict[field[4:]])
            

        # set fake values for the fields we don't have
        # last orbit
        self.metadata.setMetadataPair(metadata.METADATA_LAST_ORBIT, self.metadata.getMetadataValue(metadata.METADATA_ORBIT))
        # ascending node date
        self.metadata.setMetadataPair(metadata.METADATA_ASCENDING_NODE_DATE,  "%sT%sZ" % (self.metadata.getMetadataValue(metadata.METADATA_START_DATE),self.metadata.getMetadataValue(metadata.METADATA_START_TIME)))
        #   




    #
    #
    #
    def extractSensorMode(self):
        ptype = self.metadata.getMetadataValue(metadata.METADATA_TYPECODE)

        #MEASUREMENT=['ALD_U_N_1B','ALD_U_N_2A','ALD_U_N_2B','ALD_U_N_2C']
        #CAL=['AUX_CAL_L2']
        #CSR=['AUX_CSR_1B']
        #DCC=['AUX_DCC_1B']
        #DCMZ=['AUX_DCMZ1B']
        #HBE=['AUX_HBE_1B']

        LUT={'ALD_U_N_1B':'MEASUREMENT','ALD_U_N_2A':'MEASUREMENT','ALD_U_N_2B':'MEASUREMENT','ALD_U_N_2C':'MEASUREMENT',
             'AUX_CAL_L2':'CAL',
             'AUX_IAT_1B':'IAB',
             'AUX_CSR_1B':'CSR',
             'AUX_DCC_1B':'DCC',
             'AUX_DCMZ1B':'DCMZ',
             'AUX_HBE_1B':'HBE',
             'AUX_IDC_1B':'IDC',
             'AUX_ISR_1B':'ISR',
             'AUX_LCP_1B':'LCO',
             'AUX_LDT_1B':'LDT',
             'AUX_MRC_1B':'MRC',
             'AUX_OWV_1B':'OWV',
             'AUX_PRR_1B':'PRR',
             'AUX_RBC_L2':'RBC',
             'AUX_RRC_1B':'RRC',
             'AUX_ZWC_1B':'ZWC',
             'AUX_RDB_1B':'RDB',
             'ALD_U_N_0':'XXX',
             'ALD_U_N_0':'XXX',
             
'ALD_U_N_1A':'MEASUREMENT',
'AUX_DCC_1A':'MEASUREMENT',
'AUX_DMCZ1A':'LASER BURST WARM UP',
'AUX_IAT_1A':'CALIBRATION FAST2',
'AUX_IDC_1A':'MEASUREMENT',
'AUX_IRC_1A':'CALIBRATION SLOW',
'AUX_ISR_1A':'CALIBRATION FAST2',
'AUX_NOU_1A': 'MEASUREMENT',
'AUX_OWV_1A':'MEASUREMENT',
             
             'AUX_DCC_1A':'XXX',
             'AUX_DMCZ1A':'XXX',
             'AUX_IAT_1A':'XXX',
             'AUX_IDC_1A':'XXX',
             'AUX_IRC_1A':'XXX',
             'AUX_ISR_1A':'XXX',
             'AUX_LCP_1A':'XXX',
             'AUX_LDT_1A':'XXX',
             'AUX_NOU_1A':'XXX',
             'AUX_OWV_1A':'XXX',
             }
        sMode=None
        if LUT.has_key(ptype):
            sMode = LUT[ptype]
        else:
            print "################## extractSensorMode: productType:%s is not in LUT" % (ptype)
            #sMode = '???'
            raise Exception ("can not compute %s" % metadata.METADATA_SENSOR_OPERATIONAL_MODE)
        self.metadata.setMetadataPair(metadata.METADATA_SENSOR_OPERATIONAL_MODE, sMode)
        
        

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
        pass
        

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

