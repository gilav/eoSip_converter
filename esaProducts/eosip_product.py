# -*- coding: cp1252 -*-
#
# this class represent a EoSIP product (ZIP directory product)
#  it contains:
#  - a product 
#  - a product metadata report file
#  - zero or more browse image
#  - zero or more browse metadata report
#  - zero or one sip volume description
#
#  it use:
#  - one metadata object for the product metadata
#  - one browse_metadata object for each browse metadata
#
# This class will create a eo-sip product(not read it at this time)
# 2015/01 update: start to read an eoSip product
#
#
import os, sys, inspect
import logging
import zipfile
import traceback
from cStringIO import StringIO
from product import Product
from directory_product import Directory_Product
from namingConvention import NamingConvention
import definitions_EoSip
import xmlHelper, eosip_product_helper
import formatUtils
import browse_metadata, metadata
from definitions_EoSip import eop_EarthObservation, alt_EarthObservation, sar_EarthObservation, opt_EarthObservation, lmb_EarthObservation, atm_EarthObservation, rep_browseReport, eop_browse, SIPInfo, sipBuilder
from serviceClients import xmlValidateServiceClient
import tarfile

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# import parent
parentdir = os.path.dirname(currentdir)
print "##### eoSip converter dir:%s" % parentdir
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)
from base import processInfo

#
# list of supported validation schema type
#
BROWSE_SCHEMA_TYPE="BI"
PRODUCT_SCHEMA_TYPE="MD"
QUALITY_SCHEMA_TYPE="QR"
SIP_SCHEMA_TYPE="SI"

# ways of storing original productSRC_PRODUCT_AS_FILE="SRC_PRODUCT_AS_FILE"
SRC_PRODUCT_AS_ZIP="SRC_PRODUCT_AS_ZIP"
SRC_PRODUCT_AS_DIR="SRC_PRODUCT_AS_DIR"
SRC_PRODUCT_AS_TAR="SRC_PRODUCT_AS_TAR"
SRC_PRODUCT_AS_TGZ="SRC_PRODUCT_AS_TGZ"
SRC_PRODUCT_AS_FILE="SRC_PRODUCT_AS_FILE"


#
# list if supported services
#
SERVICE_XML_VALIDATION="xmlValidate"


class EOSIP_Product(Directory_Product):
    # browse matadata dictionnary: key=browsePath, value=browse_metadata object
    browse_metadata_dict=None
    # xml node used mapping
    xmlMappingBrowse=None
    xmlMappingMetadata=None
    # xml tag that have to be replaced
    # BROWSE_CHOICE is in browse report
    # LOCAL_ATTR is in metadata report
    NODES_AS_TEXT_BLOCK=["<BROWSE_CHOICE/>","<LOCAL_ATTR/>","<BROWSES/>","<BROWSE_CHOICE></BROWSE_CHOICE>","<LOCAL_ATTR></LOCAL_ATTR>","<BROWSES></BROWSES>"]
    # default replace text, if None it can not be defaulted.
    NODES_AS_TEXT_BLOCK_DEFAULT=["","","","","",""]

    #
    LIST_OF_SRC_PRODUCT_STORE_TYPE=[SRC_PRODUCT_AS_DIR,SRC_PRODUCT_AS_ZIP,SRC_PRODUCT_AS_TAR,SRC_PRODUCT_AS_TGZ, SRC_PRODUCT_AS_FILE]


    xmlMapping={
        #metadata.METADATA_PARENT_IDENTIFIER:'/$METADATA_TYPOLOGY$:EarthObservation/eop:metaDataProperty/eop:EarthObservationMetaData/eop:parentIdentifier'
        metadata.METADATA_START_DATE:'/phenomenonTime/TimePeriod/beginPosition',
        metadata.METADATA_STOP_DATE:'/phenomenonTime/TimePeriod/endPosition',
        metadata.METADATA_TIME_POSITION:'/resultTime/TimeInstant/timePosition',
        metadata.METADATA_PLATFORM:'/procedure/EarthObservationEquipment/platform/Platform/shortName',
        metadata.METADATA_PLATFORM_ID:'/procedure/EarthObservationEquipment/platform/Platform/serialIdentifier',
        metadata.METADATA_INSTRUMENT:'/procedure/EarthObservationEquipment/instrument/Instrument/shortName',
        metadata.METADATA_SENSOR_TYPE:'/procedure/EarthObservationEquipment/sensor/Sensor/sensorType',
        metadata.METADATA_SENSOR_OPERATIONAL_MODE:'/procedure/EarthObservationEquipment/sensor/Sensor/operationalMode',
        metadata.METADATA_RESOLUTION:'/procedure/EarthObservationEquipment/sensor/Sensor/resolution',
        metadata.METADATA_ORBIT:'/procedure/EarthObservationEquipment/acquisitionParameters/Acquisition/orbitNumber',
        metadata.METADATA_ORBIT_DIRECTION:'/procedure/EarthObservationEquipment/acquisitionParameters/Acquisition/orbitDirection',
        metadata.METADATA_WRS_LONGITUDE_GRID_NORMALISED:'/procedure/EarthObservationEquipment/acquisitionParameters/Acquisition/wrsLongitudeGrid',
        metadata.METADATA_WRS_LATITUDE_GRID_NORMALISED:'/procedure/EarthObservationEquipment/acquisitionParameters/Acquisition/wrsLatitudeGrid',
        #metadata.METADATA_WRS_LATITUDE_GRID_NORMALISED:'/procedure/EarthObservationEquipment/acquisitionParameters/Acquisition/illuminationAzimuthAngle',
        metadata.METADATA_BROWSES_TYPE:'/result/EarthObservationResult/browse/BrowseInformation/type',
        metadata.METADATA_PRODUCT_SIZE:'/result/EarthObservationResult/product/ProductInformation/size',
        metadata.METADATA_IDENTIFIER:'/metaDataProperty/EarthObservationMetaData/identifier',
        metadata.METADATA_IDENTIFIER:'/metaDataProperty/EarthObservationMetaData/identifier',
        metadata.METADATA_PARENT_IDENTIFIER:'/metaDataProperty/EarthObservationMetaData/parentIdentifier',
        metadata.METADATA_ACQUISITION_TYPE:'/metaDataProperty/EarthObservationMetaData/acquisitionType',
        metadata.METADATA_TYPECODE:'/metaDataProperty/EarthObservationMetaData/productType',
        metadata.METADATA_STATUS:'/metaDataProperty/EarthObservationMetaData/status',
        metadata.METADATA_ACQUISITION_CENTER:'/metaDataProperty/EarthObservationMetaData/downlinkedTo/DownlinkInformation/acquisitionStation',
        metadata.METADATA_PROCESSING_CENTER:'/metaDataProperty/EarthObservationMetaData/processing/ProcessingInformation/processingCenter',
        metadata.METADATA_PROCESSING_TIME:'/metaDataProperty/EarthObservationMetaData/processing/ProcessingInformation/processingDate',
        metadata.METADATA_PROCESSING_LEVEL:'/metaDataProperty/EarthObservationMetaData/processing/ProcessingInformation/processingLevel'
                }
    

    #
    # set defaults
    #
    def __init__(self, path=None):
        Directory_Product.__init__(self, path)
        
        if self.debug!=0:
            print " init class EOSIP_Product, path=%s" % path
        #
        self.browse_metadata_dict={}
        
        #
        if path!=None:
            self.path=path

        #
        self.type=Product.TYPE_EOSIP

        # the namingConvention class used
        # for sip gpackage name
        # and eo product name
        self.namingConventionSipPackage=None
        self.namingConventionEoPackage=None

        #
        # 
        # Eo product name (as in final eoSip product): is contained (as zip or tar or folder or tgz ...) inside the package
        # no extension. So == identifier
        self.eoProductName=None
        # Eo package name (as in final eoSip product): is contained (as zip or tar or folder or tgz ...) inside the package
        # has extension, like: AL1_OPER_AV2_OBS_11_20090517T025758_20090517T025758_000000_E113_N000.ZIP
        self.eoPackageName=None
        # Eo package extension
        self.eoPackageExtension=None

        # the Sip product name, has no extension
        self.sipProductName=None
        # the Sip package name, has extension
        self.sipPackageName=None
        # the Sip package extention (.ZIP normally)
        self.sipPackageExtension='ZIP'
        # the compression of the eoSip zip
        self.src_product_stored_compression=None
        # and the eo product part
        self.src_product_stored_eo_compression=None

        # the sip package full path
        self.sipPackagePath=None
        
        # the identified: product name minus extension, like: AL1_OPER_AV2_OBS_11_20090517T025758_20090517T025758_000000_E113_N000
        self.identifier=None
        #


            
        #
        # the path of the source browses that are in this EoSip
        #
        self.sourceBrowsesPath=[]
        # the source product full path
        self.sourceProductPath=None
        #
        # the browse shortName (as in final eoSip product)
        self.browses=[]
        #
        # browse file information (list or dict)
        self.browsesInfo=[]
        #
        # the generated xml reports:
        #
        # sip report xml data
        self.sipReport=None
        # the product report xml data
        self.productReport=None
        # the browse report path. A list []
        self.browsesReportPath=None
        
        #
        # NOT USED? : self.productReportName=None

        #
        #
        self.reportFullPath=None
        self.qualityReportFullPath=None
        #self.browseFullPath=None # a list []
        self.sipFullPath=None
        #
        # if product done using converter: the process information
        self.processInfo=None
        # the way the original product is stored in this eoSip
        self.src_product_stored=SRC_PRODUCT_AS_ZIP
        self.src_product_stored_compression=True

        #
        # needed to be able to read EoSip:
        #
        # AoSip helper class
        self.eoSipHelper=None
        
        # eoSip product can be:
        # - created: converter build it
        # - readed: readed from eoSip.ZIP package
        # if readed, can be worked on in some tmpDir. If so it has the flag workingOn=True
        self.created=False
        self.loaded=False
        self.workingOn=False
        self.loadedFromPath=None
        self.workingOnFolder=None
        # interresting loading message
        self.loadingMessage=None

        # eoSip loaded pieces
        self.eoPieces=[]



    #
    # add a piece
    #
    def addPiece(self, p):
        self.eoPieces.append(p)


    #
    # test if has a piece
    #
    def hasPiece(self, n):
        present=False
        for item in self.eoPieces:
            if item.name==n:
                present=True
                break
        return present

    
    #
    # get a piece
    #
    def getPiece(self, n):
        for item in self.eoPieces:
            if item.name==n:
                return item
        

    #
    # add to proces info log
    #
    def addToProcessInfoLog(self, mess):
        if self.processInfo!=None:
            self.processInfo.addLog(mess)



    #
    # set the sip package naming convention
    #
    def setNamingConventionSipInstance(self, namingConventionInstance):
        if namingConventionInstance==None:
            raise Exception("can not set Sip namingConvention because is None")
        if not isinstance(namingConventionInstance, type(NamingConvention())):
            raise Exception("Sip namingConvention is not instance of NamingConvention but:%s" % namingConventionInstance)
        self.namingConventionSipPackage=namingConventionInstance
        print " setNamingConventionSipInstance to:%s" % self.namingConventionSipPackage

        
    #
    # set the eo package naming convention
    #
    def setNamingConventionEoInstance(self, namingConventionInstance):
        if namingConventionInstance==None:
            raise Exception("can not set Eo namingConvention because is None")
        if not isinstance(namingConventionInstance, type(NamingConvention())):
            raise Exception("Eo namingConvention is not instance of NamingConvention but:%s" % namingConventionInstance)
        self.namingConventionEoPackage=namingConventionInstance
        print " setNamingConventionEoInstance to:%s" % self.namingConventionEoPackage

        
    #
    #
    #
    def getNamingConventionSipInstance(self):
        return self.namingConventionSipPackage

    #
    # load content from a EoSip product
    # test the item compression
    # try to get the MD, SI, QR, EO product pieces 
    #
    def loadProduct(self):
        # create a processInfo if not exists
        if self.processInfo==None:
            aProcessInfo=processInfo.processInfo()
            aProcessInfo.srcPath=self.path
            aProcessInfo.num=0
            # set some usefull flags
            #self.setProcessInfo(aProcessInfo)

        self.loadingMessage=''
        
        # extract sp package and name info
        self.sipPackagePath = self.path
        self.SipPackageName = formatUtils.basename(self.path)
        self.SipProductName = self.SipPackageName.replace(definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT'), '')


        
        # package name(without extension). WORKS ONLY WHEN ONE FILENAMECONVENTION USED! TODO solve pb
        # is it a .SIP.ZIP?
        pos = self.SipPackageName.find(definitions_EoSip.getDefinition('SIP'))
        if pos>0:
            print " ZIp in ZIP case"
            self.eoProductName = self.SipPackageName.replace(".%s.%s" % (definitions_EoSip.getDefinition('SIP'), definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT')), ".%s" % definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT'))
        else:
            print " NOT ZIp in ZIP case"
            self.eoProductName = self.SipPackageName.replace(definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT'), ".%s" % definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT'))


        # read zip content
        if not os.path.exists(self.path):
            raise Exception("file not found:%s" % self.path)
        self.contentList=[]
        fh = open(self.path, 'rb')
        z = zipfile.ZipFile(fh)
        n=0
        d=0
        firstLevel=True
        storeCompressedItem=0
        storeNonCompressedItem=0
        for name in z.namelist():
            n=n+1
            if self.debug!=0:
                print "  zip content[%d]:%s" % (n, name)
            if name.endswith('/'):
                d=d+1
                firstLevel=False

            # check for known parts
            piece=EoPiece(name)
            piece.compressed=self.__testZipEntryCompression(self.path, name)
            if(piece.compressed):
                storeCompressedItem=storeCompressedItem+1
            else:
                storeNonCompressedItem=storeNonCompressedItem+1

            
            if firstLevel and name.endswith(definitions_EoSip.getDefinition('MD_EXT')):
                self.reportFullPath = name
                piece.type=definitions_EoSip.getDefinition('MD_EXT')
                
            elif firstLevel and name.endswith(definitions_EoSip.getDefinition('SI_EXT')):
                self.sipFullPath = name
                piece.type=definitions_EoSip.getDefinition('SI_EXT')
                
            elif firstLevel and name.endswith(definitions_EoSip.getDefinition('QR_EXT')):
                self.qualityReportFullPath = name
                piece.type=definitions_EoSip.getDefinition('QR_EXT')

            elif firstLevel and (name.endswith(definitions_EoSip.getDefinition('JPG_EXT')) or name.endswith(definitions_EoSip.getDefinition('JPEG_EXT')) or name.endswith(definitions_EoSip.getDefinition('PNG_EXT'))):
                self.sourceBrowsesPath.append(name)
                piece.type='BI'

            elif firstLevel and name==self.eoProductName:
                self.sourceProductPath=name
                self.__testZipEntryCompression(self.path, name)
                
            self.eoPieces.append(piece)
                
            self.contentList.append(name)
        z.close()
        fh.close()
        if self.processInfo!=None:
            self.processInfo.addLog("EoSip product readed:%s" % self.path)

        self.loadingMessage="%s%s\n" % (self.loadingMessage, "zip uncompressed items:%s; compressed items:%s" % (storeNonCompressedItem, storeCompressedItem))

        self.loaded=True


    #
    #
    #
    def __testZipEntryCompression(self, path, name):
            if self.eoSipHelper==None:
                self.eoSipHelper = eosip_product_helper.Eosip_product_helper(self)
            compressed = self.eoSipHelper.isZipFileItemCompressed(path, name)
            print " #### is zip entry '%s' compressed:%s" % (name, compressed)
            return compressed

        

    #
    # start working on the product:
    # - content copied in 'workFolder/workingOn' folder
    #
    def startWorkingOn(self):
        if self.created:
            raise Exception("can not work on EoSip being created")

        self.workingOn=True
        self.processInfo.addLog("start working on EoSip:%s" % self.path)
        self.workingOnFolder = '%s/workingOn' % self.processInfo.workFolder
        
        if not os.path.exists(self.workingOnFolder): # create it
            self.addToProcessInfoLog("  will make workingOn folder:%s" % self.workingOnFolder)
            os.makedirs(self.workingOnFolder)
            self.addToProcessInfoLog("  workingOn folder created:%s\n" % (self.workingOnFolder))
        else:
            self.addToProcessInfoLog("  workingOn folder exists:%s" % self.workingOnFolder)


    #
    #
    #
    def getMetadataInfo(self):
        self.addToProcessInfoLog("################################################ getMetadataInfo")
        filename, xmlData = self.eoSipHelper.getMdPart()
        return xmlData

    #
    #
    #
    def extractMetadata(self, met=None):
        self.addToProcessInfoLog("################################################ extractMetadata")
        #
        self.loadProduct()
        #
        metContent=None
        try:
            if self.eoSipHelper==None:
                self.eoSipHelper = eosip_product_helper.Eosip_product_helper(self)
            self.addToProcessInfoLog("################################################ eoSipHelper created")
            metContent = self.getMetadataInfo()
            print "metContent=%s" % metContent
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print " ERROR getting metadata info:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())

        # get typology
        typology=self.eoSipHelper.getTypologyFromMdContent(metContent) # is like: eop, sar, lmb...
        # set in ingester as supported type: EOP, SAR, LMB...
        supportedTypology=None
        n=0
        for item in sipBuilder.TYPOLOGY_REPRESENTATION:
            #print "compare:'%s<->%s'" % (item, typology)
            if item==typology:
                supportedTypology=sipBuilder.TYPOLOGY_REPRESENTATION
                break
            n=n+1

        if supportedTypology==None:
            raise Exception("unknown typology:%s" % typology)
        
        if self.processInfo != None and self.processInfo.ingester!=None:
            self.processInfo.ingester.TYPOLOGY=sipBuilder.TYPOLOGY_REPRESENTATION_SUFFIX[n]
        met.setMetadataPair(metadata.METADATA_TYPOLOGY, typology)
        self.addToProcessInfoLog("################################################ typology:%s" % typology)
            
        # extact metadata
        helper=xmlHelper.XmlHelper()
        helper.setData(metContent);
        helper.parseData()
        self.addToProcessInfoLog("################################################ extractMetadata: xml parsed")

        #print "@@@@@@@@@@@@@@@@@@@ metadata dump:%s" % (met.toString())

        #get fields
        resultList=[]
        op_element = helper.getRootNode()
        num_added=0

        reportBuilder=eop_EarthObservation.eop_EarthObservation()
        for field in self.xmlMapping:
            # take care of the case we have a metadata name in the path: like '/...../....../$TYPECODE$_abcd/.../'
            mapping = self.xmlMapping[field]
            mappingOk=mapping
            pos = mappingOk.find('$')
            if pos>=0:
                #print "@@@@@@@@@@@@@@@@@@@ metadataName mapping pos=%s" % pos
                pos2=mappingOk.find('$', pos+1)
                #print "@@@@@@@@@@@@@@@@@@@ metadataName mapping pos2=%s" % pos2
                if pos2>0:
                    metadataName=mappingOk[pos+1:pos2]
                    #print "@@@@@@@@@@@@@@@@@@@ metadataName:%s" % (metadataName)
                    value = met.getMetadataValue(metadataName)
                    #print "@@@@@@@@@@@@@@@@@@@ metadataName value:%s" % value
                    mappingOk = mapping.replace("$%s$" % metadataName, value)
                    #print "@@@@@@@@@@@@@@@@@@@ mappingOk:%s" % (mappingOk)
                #else:
                    #print "@@@@@@@@@@@@@@@@@@@ metadataName no mapping pos2"
            #else:
                #print "@@@@@@@@@@@@@@@@@@@ metadataName no mapping pos"   

            
            # attribute case
            if mappingOk.find("@")>=0:
                attr=mappingOk.split('@')[1]
                path=mappingOk.split('@')[0]
            else:
                attr=None
                path=mappingOk

            #
            if self.debug==0:
                print "  xml node path:%s" % (path)
                
            #helper.DEBUG=1
            aData = helper.getFirstNodeByPath(None, path, None)
            if aData==None:
                aValue=None
            else:
                if attr==None:
                    aValue=helper.getNodeText(aData)
                else:
                    aValue=helper.getNodeAttributeText(aData,attr)        

            if self.debug==0:
                print "  -->%s=%s" % (field, aValue)
            met.setMetadataPair(field, aValue)
            num_added=num_added+1


        self.metadata=met
        # refine metadata
        self.refineMetadata()
        
        return 0


    #
    # refine the metada
    #
    def refineMetadata(self):
        # separate date and time from datatTimeZ
        tmp=self.metadata.getMetadataValue(metadata.METADATA_START_DATE)
        tmp1=self.metadata.getMetadataValue(metadata.METADATA_STOP_DATE)
        date=tmp.split('T')[0]
        time=tmp.split('T')[1].replace('Z','')
        self.metadata.setMetadataPair(metadata.METADATA_START_DATE, date)
        self.metadata.setMetadataPair(metadata.METADATA_START_TIME, time)
        print "######### start date:%s  time:%s" % (date, time)
                                      
        date=tmp1.split('T')[0]
        time=tmp1.split('T')[1].replace('Z','')
        self.metadata.setMetadataPair(metadata.METADATA_STOP_DATE, date)
        self.metadata.setMetadataPair(metadata.METADATA_STOP_TIME, time)
        print "######### stop date:%s  time:%s" % (date, time)

        # set track and frame
        tmp=self.metadata.getMetadataValue(metadata.METADATA_WRS_LONGITUDE_GRID_NORMALISED)
        self.metadata.setMetadataPair(metadata.METADATA_TRACK, tmp)
        tmp=self.metadata.getMetadataValue(metadata.METADATA_WRS_LATITUDE_GRID_NORMALISED)
        self.metadata.setMetadataPair(metadata.METADATA_FRAME, tmp)


    #
    # how will we store the source product in the destination eoSip? ZIP, TGZ,...
    #
    def setSrcProductStoreType(self, t):
        self.LIST_OF_SRC_PRODUCT_STORE_TYPE.index(t)
        self.src_product_stored=t


    #
    #
    #
    def getSrcProductStoreType(self):
        return self.src_product_stored


    #
    # set if the eoSip zip compressed
    #
    def setSrcProductStoreCompression(self, b):
        self.src_product_stored_compression = b


    #
    #
    #
    def getSrcProductStoreCompression(self):
        return self.src_product_stored_compression


    #
    # set if the eo product is compressed
    #
    def setSrcProductStoreEoCompression(self, b):
        self.src_product_stored_eo_compression = b


    #
    #
    #
    def getSrcProductStoreEoCompression(self):
        return self.src_product_stored_eo_compression


    #
    #
    #
    def setXmlMappingMetadata(self, dict1, dict2):
        self.xmlMappingMetadata=dict1
        self.xmlMappingBrowse=dict2
        # put it in metadata
        self.metadata.xmlNodeUsedMapping=dict1

 
    #
    #
    #
    def setProcessInfo(self, p):
        self.processInfo=p


    #
    #
    #
    def setProcessInfo(self, p):
        self.processInfo=p


    #
    #
    #
    def getProcessInfo(self):
        return self.processInfo



    #
    # add a source browse, create the corresponding report info
    #
    def addSourceBrowse(self, path=None, addInfo=None):
        if self.debug!=0:
            print "#############$$$$$$$$$$$$$$$ add source browse file[%d]:%s" % (len(self.sourceBrowsesPath), path)
            print "#############$$$$$$$$$$$$$$$ add source browse info[%d]:%s" % (len(self.browsesInfo), addInfo)
        #self.browseFullPath=[]
        self.sourceBrowsesPath.append(path)
        self.browsesInfo.append(addInfo)
        shortName=os.path.split(path)[1]
        # create browse metadata info
        bMet=browse_metadata.Browse_Metadata()
        # set typology
        bMet.setOtherInfo("TYPOLOGY_SUFFIX", self.metadata.getOtherInfo("TYPOLOGY_SUFFIX"))
        
        # set xml node used map
        bMet.xmlNodeUsedMapping=self.xmlMappingBrowse

        
        bMet.setMetadataPair(browse_metadata.BROWSE_METADATA_FILENAME, shortName)
        pos=shortName.rfind('.')
        tmp=shortName
        if pos >=0:
            tmp=tmp[0:pos]
        bMet.setMetadataPair(browse_metadata.BROWSE_METADATA_NAME, tmp)
        # set matadata for browse: these one are the same as for product
        bMet.setMetadataPair(metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER, self.metadata.getMetadataValue(metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER))
        bMet.setMetadataPair(metadata.METADATA_START_DATE, self.metadata.getMetadataValue(metadata.METADATA_START_DATE))
        bMet.setMetadataPair(metadata.METADATA_START_TIME, self.metadata.getMetadataValue(metadata.METADATA_START_TIME))
        bMet.setMetadataPair(metadata.METADATA_STOP_DATE, self.metadata.getMetadataValue(metadata.METADATA_STOP_DATE))
        bMet.setMetadataPair(metadata.METADATA_STOP_TIME, self.metadata.getMetadataValue(metadata.METADATA_STOP_TIME))
        # change last 2 last typecode digit in: BP
        tmp=self.metadata.getMetadataValue(metadata.METADATA_TYPECODE)
        tmp=tmp[0:len(tmp)-2]
        tmp="%sBP" % tmp
        #bMet.setMetadataPair(browse_metadata.BROWSE_METADATA_BROWSE_TYPE, self.metadata.getMetadataValue(metadata.METADATA_TYPECODE))
        bMet.setMetadataPair(browse_metadata.BROWSE_METADATA_BROWSE_TYPE, tmp)
        #
        bMet.setMetadataPair('METADATA_GENERATION_TIME', self.metadata.getMetadataValue(metadata.METADATA_GENERATION_TIME))
        bMet.setMetadataPair('METADATA_RESPONSIBLE', self.metadata.getMetadataValue('METADATA_RESPONSIBLE'))
        bMet.setMetadataPair('BROWSE_METADATA_IMAGE_TYPE', self.metadata.getMetadataValue('BROWSE_METADATA_IMAGE_TYPE'))
        self.browse_metadata_dict[path]=bMet
        

    #
    #
    #
    def setEoExtension(self, ext):
        self.eoPackageExtension = ext


    #
    #
    #
    def setSipExtension(self, ext):
        self.sipProductExtension = ext



    #
    # build the product metadata report, running the class rep_metadataReport
    #
    def buildProductReportFile(self):
        if self.debug==0:
            print "\n build product metadata report"
            print " Eo-Sip metadata dump:\n%s" % self.metadata.toString()

        # make the report xml data
        #productReportBuilder=rep_metadataReport.rep_metadataReport()
        #xmldata=productReportBuilder.buildMessage(self.metadata, "rep:metadataReport")
        # change for OGC spec: root node is the specialized EarthObservation
        ##productReportBuilder=eop_EarthObservation.eop_EarthObservation()
        #self.metadata.debug=1
        typologyUsed = self.metadata.getOtherInfo("TYPOLOGY_SUFFIX")
        if self.debug!=0:
            print "############## typologyUsed:"+typologyUsed
        if typologyUsed=='':
            typologyUsed='EOP'
            
        if typologyUsed=='EOP':
            productReportBuilder=eop_EarthObservation.eop_EarthObservation()
        elif typologyUsed=='OPT':
            productReportBuilder=opt_EarthObservation.opt_EarthObservation()
        elif typologyUsed=='ALT':
            productReportBuilder=alt_EarthObservation.alt_EarthObservation()
        elif typologyUsed=='LMB':
            productReportBuilder=lmb_EarthObservation.lmb_EarthObservation()
        elif typologyUsed=='SAR':
             productReportBuilder=sar_EarthObservation.sar_EarthObservation()
        #
        #productReportBuilder.debug=0
        xmldata=productReportBuilder.buildMessage(self.metadata, "%s:EarthObservation" % typologyUsed.lower())


        # add the BROWSE block. just for first browse (if any) at this time. TODO: loop all browses?
        if len(self.browse_metadata_dict)>0:
            print "there is browse"
            bmet=self.browse_metadata_dict.values()[0]
            if self.debug!=0:
                print "%%%%%%%%%%%%%%%%%%%% BMET DUMP:%s" % bmet.dump()

            browseBlockBuilder=eop_browse.eop_browse()
            #browseReportBuilder.debug=1
            browseBlock=browseBlockBuilder.buildMessage(bmet, "eop:browse")
            if self.debug<10:
                print " browseBlock content:\n%s" % browseBlock
            if xmldata.find('<BROWSES></BROWSES>')>0:
                xmldata=xmldata.replace('<BROWSES></BROWSES>', browseBlock)
            elif xmldata.find('<BROWSES/>')>0:
                xmldata=xmldata.replace('<BROWSES/>', browseBlock)
        else:
            print "there is no browse"


        # add the local attributes
        attr=self.metadata.getLocalAttribute()
        #print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ length localattributes:%s" % len(attr)
        if len(attr) > 0:
            n=0
            res="" #<eop:vendorSpecific><eop:SpecificInformation>"
            for adict in attr:
                key=adict.keys()[0]
                value=adict[key]
                #print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ localattributes[%d]: %s=%s" % (n, key, value)
                res = "%s<eop:vendorSpecific><eop:SpecificInformation><eop:localAttribute>%s</eop:localAttribute><eop:localValue>%s</eop:localValue></eop:SpecificInformation></eop:vendorSpecific>" % (res, key, value)
                    
                n=n+1
            #print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ localattributes block:%s" % res
            pos = xmldata.find("<LOCAL_ATTR></LOCAL_ATTR>")
            if pos >= 0:
                xmldata=xmldata.replace("<LOCAL_ATTR></LOCAL_ATTR>", res)
            #else:
            #    print " @@@@@@@@@@@@@@@@@@@@@@@@@ !!!!!!!!!!!!!!!!!!! no <LOCAL_ATTR></LOCAL_ATTR> block found"
            
        

        # sanitize test
        tmp=self.productReport=self.sanitizeXml(xmldata)
        
        # verify xml, build file name
        self.productReport=self.formatXml(tmp, self.folder, 'product_report')
        if self.debug!=0:
            print " product report content:\n%s" % self.productReport
        ext=definitions_EoSip.getDefinition("MD_EXT")
        reportName="%s.%s" % (self.eoProductName, ext)
        if self.debug!=0:
            print "   product report name:%s" % (reportName)

        # sanitize test
        #self.productReport=self.sanitizeXml(self.productReport)
            
        # write it
        self.reportFullPath="%s/%s" % (self.folder, reportName)
        fd=open(self.reportFullPath, "wb")
        fd.write(self.productReport)
        fd.flush()
        fd.close()
        if self.debug!=0:
            print "   product report written at path:%s" % self.reportFullPath

        if self.processInfo.verify_xml:
            print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@################ call external xml validator:%s" % self.processInfo.verify_xml 
            # call xml validator service
            validator = xmlValidateServiceClient.XmlValidateServiceClient(self.processInfo)
            validator.useXmlValidateService(self.processInfo, PRODUCT_SCHEMA_TYPE, self.reportFullPath)
        else :
            print " dont use external xml validator" 
            
        return self.reportFullPath


    #
    # build the browse metadata reports
    # one per browse
    #
    # return the filename of the browse report files
    #
    def buildBrowsesReportFile(self):
        #if self.debug!=0:
        if self.debug!=0:
            print " build browse metadata reports"
        #
        
        n=0
        browseReport=None
        browseReportName=None
        self.browsesReportPath=[]
        i=0
        for browsePath in self.sourceBrowsesPath:
            bmet=self.browse_metadata_dict[browsePath]
            if self.debug!=0:
                print " build browse metadata report[%d]:%s\n%s" % (n, browsePath, bmet.toString())
                
            #
            browseReportName="%s.%s" % (bmet.getMetadataValue(browse_metadata.BROWSE_METADATA_NAME), definitions_EoSip.getDefinition('XML_EXT'))
            bmet.setMetadataPair(browse_metadata.BROWSE_METADATA_REPORT_NAME, browseReportName)
            if self.debug!=0:
                print "  browse metadata report[%d] name:%s" % (n, browseReportName)
                
            browseReportBuilder=rep_browseReport.rep_browseReport()
            #browseReportBuilder.debug=1
            browseReport=self.formatXml(browseReportBuilder.buildMessage(bmet, "rep:browseReport"), self.folder, 'browse_report_%d' % i)
            
            # add BROWSE_CHOICE block, original block may have be altered by prettyprint...
            if browseReport.find('<BROWSE_CHOICE></BROWSE_CHOICE>')>0:
                browseReport=browseReport.replace('<BROWSE_CHOICE></BROWSE_CHOICE>', bmet.getMetadataValue(browse_metadata.BROWSE_METADATA_BROWSE_CHOICE))
            elif browseReport.find('<BROWSE_CHOICE/>')>0:
                browseReport=browseReport.replace('<BROWSE_CHOICE/>', bmet.getMetadataValue(browse_metadata.BROWSE_METADATA_BROWSE_CHOICE))
            if self.debug!=0:
                print " browse report content:\n%s" % browseReport

            # test
            browseReport=self.sanitizeXml(browseReport)
            browseReport=self.formatXml(browseReport, self.folder, 'browse')
            
            #
            # write it
            thisBrowseReportFullPath="%s/%s" % (self.folder, browseReportName)
            self.browsesReportPath.append(thisBrowseReportFullPath)
            #print " browse report content:\n%s" % browseReport
            fd=open(thisBrowseReportFullPath, "wb")
            fd.write(browseReport)
            fd.flush()
            fd.close()
            if self.debug!=0:
                print "   browse report written at path:%s" % thisBrowseReportFullPath

            if self.processInfo.verify_xml:
                print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@################ call external xml validator:%s" % self.processInfo.verify_xml 
                # call xml validator service
                validator = xmlValidateServiceClient.XmlValidateServiceClient(self.processInfo)
                validator.useXmlValidateService(self.processInfo, BROWSE_SCHEMA_TYPE, thisBrowseReportFullPath)
            else :
                print " dont use external xml validator" 
                
            i=i+1
                
        return self.browsesReportPath


    #
    # build the sip report
    #
    def buildSipReportFile(self):
        if self.debug!=0:
            print " build sip report"

        #
        self.info()

        
        #
        #reportFolderName=os.path.split(self.sourceBrowsesPath[0])[0]
        #reportFolderName=self.folder
        #
        sipReportBuilder=SIPInfo.SIPInfo()
        self.sipReport=self.formatXml(sipReportBuilder.buildMessage(self.metadata, "SIPInfo"), self.folder, 'sip_report')
        if self.debug!=0:
            print " sip report content:\n%s" % self.sipReport
        ext=definitions_EoSip.getDefinition("SI_EXT")
        sipName="%s.%s" % (self.eoProductName, ext)
        if self.debug!=0:
            print "   sip report name:%s" % (sipName)

        #
        self.sipReport=self.sanitizeXml(self.sipReport)
            
        # write it
        self.sipFullPath="%s/%s" % (self.folder, sipName)
        fd=open(self.sipFullPath, "wb")
        fd.write(self.sipReport)
        fd.flush()
        fd.close()
        if self.debug!=0:
            print "   sip report written at path:%s" % self.sipFullPath
            
        return self.sipFullPath
        

    #
    #
    #
    def getOutputFolders(self, basePath=None, final_path_list=None):                
            #create directory trees according to the configuration path rules
            if self.debug!=0:
                print "  getOutputFolders: basePath=%s, final_path_list=%s" % (basePath, final_path_list)
            folders=[]
            if basePath[-1]!='/':
                    basePath="%s/" % basePath
            if len(final_path_list)==0:
                    raise Exception("final_path_list is empty")
            i=0
            blocks=final_path_list.split(',')
            for rule in blocks:
                    if rule[0]=='[':
                        rule=rule[1:]
                    if rule[-1]==']':
                        rule=rule[0:-1]
                    rule=rule.replace('"','')
                    if self.debug!=0:
                        print "  resolve path rule[%d/%d]:%s" % (i,len(blocks), rule)
                    toks=rule.split('/')
                    new_rulez = basePath
                    n=0
                    for tok in toks:
                            new_rulez="%s%s/" % (new_rulez, self.metadata.eval(tok))
                            n=n+1
                    if self.debug!=0:
                        print "  resolved path rule[%d]:%s" % ( i, new_rulez)
                    folders.append(new_rulez)
                    i=i+1
            return folders


    #
    # store EoProduct in the EoSip ZIP package as file(s)
    #
    # AT THIS TIME: store workfolder files
    #
    def writeEoProductAsFile(self, zipf):
            self.processInfo.addLog("eoSip store as FILE")
            # 
            for name in self.processInfo.srcProduct.contentList:
                self.processInfo.addLog("eoSip store:%s" % name)
                # test if the file is in the workfolder, or if it is a reference in a piece
                piece=None
                localPath="%s/%s" % (self.processInfo.workFolder, name)
                alias=name
                if self.hasPiece(name): # a piece
                    piece = self.getPiece(name)

                    if piece.localPath!=None:
                        localPath=piece.localPath
                        self.processInfo.addLog(" is a piece: localPath=%s" % localPath)
                    if piece.alias!=None:
                        alias=piece.alias
                        self.processInfo.addLog("  has a alias=%s" % alias)
                
                if self.src_product_stored_eo_compression==True:
                    self.processInfo.addLog("deflated: %s" % name)
                    zipf.write(localPath, "%s" % (alias), zipfile.ZIP_DEFLATED)
                else:
                    self.processInfo.addLog("stored: %s" % alias)
                    zipf.write(localPath, "%s" % (alias), zipfile.ZIP_STORED)
                    

    #
    # store EoProduct in the EoSip ZIP package as directory
    #
    # AT THIS TIME: store workfolder files
    #
    def writeEoProductAsDir(self, zipf):
            self.processInfo.addLog("eoSip store as DIR")
            # 
            for name in self.processInfo.srcProduct.contentList:
                self.processInfo.addLog("eoSip store:%s" % name)
                if self.src_product_stored_eo_compression==True:
                    self.processInfo.addLog("deflated: %s" % name)
                    zipf.write("%s/%s" % (self.processInfo.workFolder, name), "%s/%s" % (self.eoProductName, name), zipfile.ZIP_DEFLATED)
                else:
                    self.processInfo.addLog("stored: %s" % name)
                    zipf.write("%s/%s" % (self.processInfo.workFolder, name), "%s/%s" % (self.eoProductName, name), zipfile.ZIP_STORED)
                zipf.flush()


    #
    # store EoProduct in the EoSip ZIP package as ZIP file
    #
    # AT THIS TIME: store source file
    #
    # two case:
    # - source is already a zip file ==> just rename it
    # - source is not a zip file ==> compress(or not) into a zip
    #
    def writeEoProductAsZip(self, zipf):
            self.processInfo.addLog("eoSip store as ZIP")
            # source product is ZIP case
            if self.sipPackageName.endswith("%s.%s" % (definitions_EoSip.getDefinition('SIP'), definitions_EoSip.getDefinition('PACKAGE_EXT'))):

                self.processInfo.addLog("eoSip store source zip file: %s" % self.eoPackageName)
                self.writeInZip(zipf, self.sourceProductPath, self.eoPackageName, self.src_product_stored_eo_compression)
                
            else: # zip source product, at this time: assume it is a single file
                self.processInfo.addLog("eoSip store source file")
                tmpProductZippedPath="%s/productZipped.zip" % (self.folder)
                zipTmpProduct = zipfile.ZipFile(tmpProductZippedPath, 'w')
                if self.src_product_stored_eo_compression==True:
                    zipTmpProduct.write(self.sourceProductPath, os.path.split(self.sourceProductPath)[1], zipfile.ZIP_DEFLATED)
                    self.processInfo.addLog("deflated: %s" % self.sourceProductPath)
                else:
                    zipTmpProduct.write(self.sourceProductPath, os.path.split(self.sourceProductPath)[1], zipfile.ZIP_STORED)
                    self.processInfo.addLog("stored: %s" % self.sourceProductPath)
                zipTmpProduct.flush()
                zipTmpProduct.close()
                if self.src_product_stored_eo_compression==True:
                    zipf.write(tmpProductZippedPath, self.eoProductName, zipfile.ZIP_DEFLATED)
                    self.processInfo.addLog("deflated: %s" % self.sourceProductPath)
                else:
                    zipf.write(tmpProductZippedPath, self.eoProductName, zipfile.ZIP_STORED)
                    self.processInfo.addLog("stored: %s" % self.sourceProductPath)
                zipf.flush()


    #
    # store EoProduct in the EoSip ZIP package as TGZ
    #
    # AT THIS TIME: store workfolder files
    #
    def writeEoProductAsTgz(self, zipf):
            self.processInfo.addLog("eoSip store as TGZ")
            
            # create a temporary tar file
            tar=None
            tmpProductTarredPath=None
            # 
            tmpProductTarredPath="%s/%s.%s" % (self.folder, self.eoProductName, definitions_EoSip.getDefinition('TAR_EXT'))
            if os.path.exists(tmpProductTarredPath):
                os.remove(tmpProductTarredPath)
            #
            if self.src_product_stored_eo_compression==True:
                tar = tarfile.open(tmpProductTarredPath, "w:gz")
            else:
                tar = tarfile.open(tmpProductTarredPath, "w")

            for name in self.processInfo.srcProduct.contentList:
                if self.src_product_stored_eo_compression==True:
                    self.processInfo.addLog("deflated: %s" % name)
                    tar.add("%s/%s" % (self.processInfo.workFolder, name), name)
                else:
                    self.processInfo.addLog("stored: %s" % name)
                    tar.add("%s/%s" % (self.processInfo.workFolder, name), name)
            tar.flush()
            tar.close()
            
            # if compressed rename as TGZ
            if self.src_product_stored_eo_compression==True:
                tmpProductTarredPath1 = tmpProductTarredPath.replace(definitions_EoSip.getDefinition('TAR_EXT'), definitions_EoSip.getDefinition('TGZ_EXT'))
                if os.path.exists(tmpProductTarredPath1):
                    os.remove(tmpProductTarredPath1)
                os.rename(tmpProductTarredPath, tmpProductTarredPath1)
                tmpProductTarredPath = tmpProductTarredPath1
            

            # add temporary tar in zip
            if self.src_product_stored_eo_compression==True:
                zipf.write(tmpProductTarredPath, self.eoPackageName, zipfile.ZIP_DEFLATED)
                self.processInfo.addLog("deflated: %s" % tmpProductTarredPath)
            else:
                zipf.write(tmpProductTarredPath, self.eoPackageName, zipfile.ZIP_STORED)
                self.processInfo.addLog("stored: %s" % tmpProductTarredPath)
            zipf.flush()



    #
    # wtite the Eo-Sip package in a folder.
    # p: path of the output folder
    #
    def writeToFolder(self, p=None, overwrite=None):
        if self.eoProductName==None:
            raise Exception("Eo-Sip product has no productName")
        if self.debug==0:
            print "\n will write EoSip product at folder path:%s" % p
        if p[-1]!='/':
            p=p+'/'

        #
        self.path="%s%s" % (p, self.sipPackageName)
        if self.debug==0:
            print " full eoSip path:%s" % self.path

        # already exists?
        if os.path.exists(self.path) and (overwrite==None or overwrite==False):
                raise Exception("refuse to overwite existing product:%s" % self.path)

        # create folder neeedd
        if not os.path.exists(p):
            os.makedirs(p)

        # remove precedent zip if any
        if os.path.exists(self.path):
            os.remove(self.path)
        
        # create zip
        zipf = zipfile.ZipFile(self.path, 'w')
        
        # write product itself
        if self.debug!=0:
            print "  write EoSip content[0]; product itself:%s  as:%s" % (self.sourceProductPath, self.eoProductName)

        #
        # two case:
        # - source is already a zip file ==> just rename it
        # - source is not a zip file ==> compress(or not) into a zip
        print " @@@@@@@@@@@@@@ will store original product as:%s" % self.src_product_stored
        self.processInfo.addLog("eoSip store type:%s" % self.src_product_stored)
        self.processInfo.addLog("eoSip store compression:%s" % self.src_product_stored_compression)
        self.processInfo.addLog("eoSip store compression flag type is bool?:%s" % isinstance(self.src_product_stored_compression, bool))


        # NEW CODE:
        # store as FILES       
        if self.src_product_stored==SRC_PRODUCT_AS_FILE:
            self.writeEoProductAsFile(zipf)
        
        # store as ZIP       
        elif self.src_product_stored==SRC_PRODUCT_AS_ZIP:
            self.writeEoProductAsZip(zipf)

        # store as FOLDER
        elif self.src_product_stored==SRC_PRODUCT_AS_DIR:
            self.writeEoProductAsDir(zipf)

        # store as TGZ
        elif self.src_product_stored==SRC_PRODUCT_AS_TGZ:
            self.writeEoProductAsTgz(zipf)

        # store as TAR
        elif self.src_product_stored==SRC_PRODUCT_AS_TAR:
            self.writeEoProductAsTgz(zipf)

        # store as FOLDER. old code disabled
        elif self.src_product_stored=='disabled_if': #SRC_PRODUCT_AS_DIR:
            self.processInfo.addLog("eoSip store as DIR")
            # 
            for name in self.processInfo.srcProduct.contentList:
                self.processInfo.addLog("eoSip store:%s" % name)
                if self.src_product_stored_compression==True:
                    self.processInfo.addLog("deflated: %s" % name)
                    zipf.write("%s/%s" % (self.processInfo.workFolder, name), "%s/%s" % (self.eoProductName, name), zipfile.ZIP_DEFLATED)
                else:
                    self.processInfo.addLog("stored: %s" % name)
                    zipf.write("%s/%s" % (self.processInfo.workFolder, name), "%s/%s" % (self.eoProductName, name), zipfile.ZIP_STORED)
            zipf.flush()
                    
        else:
            raise Exception("unsuported store type:%s" % self.src_product_stored)
                    


        # write browses images + reports
        for browsePath in self.sourceBrowsesPath:
            folder=os.path.split(browsePath)[0]
            bmet=self.browse_metadata_dict[browsePath]
            #
            extension = formatUtils.getFileExtension(browsePath)
            name= "%s.%s" % (self.eoProductName, extension)
            if self.processInfo.test_dont_do_browse!=True:
                if self.debug==0:
                    print "   write EoSip browse[n]:%s  as:%s" % (browsePath, name)                                                                 
                if self.src_product_stored_compression==True:
                    zipf.write(browsePath, name, zipfile.ZIP_DEFLATED)
                    self.processInfo.addLog("deflated: %s" % name)
                else:
                    zipf.write(browsePath, name, zipfile.ZIP_STORED)
                    self.processInfo.addLog("stored: %s" % name)
            else:
                print "   dont' do browse flag is set, so don't write EoSip browse[n]:%s  as:%s" % (browsePath, name)   
                
            # if we have build the browse reports
            if self.browsesReportPath != None:
                name=bmet.getMetadataValue(browse_metadata.BROWSE_METADATA_REPORT_NAME)
                path = "%s/%s" % (folder, name)
                if self.src_product_stored_compression==True:
                    zipf.write(path, name, zipfile.ZIP_DEFLATED)
                    self.processInfo.addLog("deflated: %s" % name)
                else:
                    zipf.write(path, name, zipfile.ZIP_STORED)
                    self.processInfo.addLog("stored: %s" % name)
        #

        # write product reports
        if self.src_product_stored_compression==True:
            zipf.write(self.reportFullPath, os.path.split(self.reportFullPath)[1], zipfile.ZIP_DEFLATED)
            self.processInfo.addLog("deflated: %s" % os.path.split(self.reportFullPath)[1])
        else:
            zipf.write(self.reportFullPath, os.path.split(self.reportFullPath)[1], zipfile.ZIP_STORED)
            self.processInfo.addLog("stored: %s" % os.path.split(self.reportFullPath)[1])
            
        # write sip report
        if self.sipReport!=None:
            if self.src_product_stored_compression==True:
                zipf.write(self.sipFullPath, os.path.split(self.sipFullPath)[1], zipfile.ZIP_DEFLATED)
                self.processInfo.addLog("deflated: %s" % os.path.split(self.sipFullPath)[1])
            else:
                zipf.write(self.sipFullPath, os.path.split(self.sipFullPath)[1], zipfile.ZIP_STORED)
                self.processInfo.addLog("stored: %s" % os.path.split(self.sipFullPath)[1])
        zipf.flush()
        zipf.close()


    #
    # control that the xml is well formatted, if not save it on disk
    #
    def formatXml(self, data=None, path=None, type=None):
        res=None
        try:
            # pretty print it
            helper=xmlHelper.XmlHelper()
            helper.parseData(data)
            # this will verify that xml is correct:
            res=helper.prettyPrintAll()
            #print "pretty print xml:\n%s" % res
            # keep original format, because is already indexed, to avoid mess with helper.prettyPrint()
            #res=data
            #res=self.sanitizeXml(data)
            
        except Exception, e:
            # write it for debug
            path="%s/faulty_%s.xml" % (path, type)
            print "xml faulty %s data dump at path:%s" % (type, path)
            print "\n\n\n%s\n\n\n" % data
            fd=open(path, 'w')
            fd.write(data)
            fd.flush()
            fd.close()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print "xml format error: %s   %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
            raise e
        return res


    #
    # verify that the xml doesn't have anymore BLOCK_NODE that should have been substituted
    # if there still are, default them if possible
    # if not, raise error
    #
    def sanitizeXml(self, mess):
        n=0
        for pattern in self.NODES_AS_TEXT_BLOCK:
            pos=mess.find(pattern)
            if pos>0:
                print " @@@@@@@@@@@@@@@ sanitizeXml: pattern[%d]:'%s' found at pos:%s; can be substituted with:'%s'" % (n, pattern, pos, self.NODES_AS_TEXT_BLOCK_DEFAULT[n])
                if self.NODES_AS_TEXT_BLOCK_DEFAULT[n]==None:
                    raise Exception("sanitizeXml: block %s can not be defaulted!" % pattern)
                else:
                    # TODO: should delete backward up to precedent newline...
                    mess=mess.replace(pattern, self.NODES_AS_TEXT_BLOCK_DEFAULT[n])
                
            n=n+1
                
        return mess
        

    #
    # build package and peoductname
    # namingConvention is the class instance used
    # ext is the extension of the eoProduct (what is inside the eoSip package),if not specified, use default EoSip extension: .ZIP
    #
    def buildEoNames(self, namingConvention=None): #, ext=None, eoExt=None ):
        if self.src_product_stored!=SRC_PRODUCT_AS_FILE and self.src_product_stored!=SRC_PRODUCT_AS_DIR and self.eoPackageExtension==None:
            raise Exception("eoPackageExtension not defined")
        
        if self.namingConventionSipPackage==None:
            raise Exception("namingConvention sip instance is None")

        if self.namingConventionEoPackage==None:
            raise Exception("namingConvention eo instance is None")
        
        if self.debug==0:
            print " build eo product names, pattern=%s, eoExt=%s, sipExt=%s" % (self.namingConventionEoPackage.usedPattern, self.eoPackageExtension, self.sipPackageExtension)

        # build sip product and package names
        if self.debug==0:
            print " build sip product names, pattern=%s,ext=%s" % (self.namingConventionSipPackage.usedPattern, self.sipPackageExtension) 
        self.sipPackageName=self.namingConventionSipPackage.buildProductName(self.metadata, self.sipPackageExtension)
        print "self.sipPackageName:%s" % self.sipPackageName
        self.sipProductName=self.sipPackageName.split('.')[0]
        print "self.sipProductName:%s" % self.sipProductName


        # build eoProductName
        # eoProductName coulb be already defined, in case we want to keep original product name for example
        # in this case, we don't change it
        if self.debug==0:
            print " build eo product names, pattern=%s,ext=%s" % (self.namingConventionEoPackage.usedPattern, self.eoPackageExtension)  
        tmpEoProductName=self.namingConventionEoPackage.buildProductName(self.metadata, self.eoPackageExtension)
        print "tmpEoProductName:%s" % tmpEoProductName
        eoNameDefined=False
        if self.eoProductName==None:
            self.eoPackageName=tmpEoProductName
            self.eoProductName=tmpEoProductName.split('.')[0]
            eoNameDefined=True
            self.processInfo.addLog(" eo product name built")
            
        else:
            # if we have aht extension in eoProductName, set the choosed one
            pos = self.eoProductName.find('.')
            if pos<0:
                self.eoPackageName="%.%s" % (self.eoProductName, self.eoPackageExtension)
            else:
                self.eoPackageName="%s.%s" % (self.eoProductName[0:pos], self.eoPackageExtension)
                self.eoProductName=self.eoProductName[0:pos]
            self.processInfo.addLog(" eo product predifined, use it:  eo product name=%s\n eo product name=%s" % (self.eoProductName, self.sipProductName))
            

            
            
        #
        self.identifier=self.eoProductName
        self.metadata.setMetadataPair(metadata.METADATA_PRODUCTNAME, self.eoProductName)
        self.metadata.setMetadataPair(metadata.METADATA_PACKAGENAME, self.sipProductName)
        if self.debug==0:
            print " ==> builded product/package product=%s; package=%s" % (self.eoProductName, self.sipProductName)

        if eoNameDefined and self.eoPackageExtension==definitions_EoSip.getDefinition('PACKAGE_EXT'):
            # if eoProduct is inside ZIP and his filename is not the original filename, set sipPackage to .SIP.ZIP
            #if self.eoPackageExtension==definitions_EoSip.getDefinition('PACKAGE_EXT'):
            print " #################################################################### we are in zip in zip case: use .SIP.ZIP for eo package name"
            self.sipPackageName = "%s.%s.%s" % (self.sipProductName, definitions_EoSip.getDefinition('SIP'), definitions_EoSip.getDefinition('PACKAGE_EXT'))
        else:
            print " #################################################################### we are NOT in zip in zip case"
            self.sipPackageName = "%s.%s" % (self.sipProductName, self.sipPackageExtension)
                
        self.metadata.setMetadataPair(metadata.METADATA_IDENTIFIER, self.identifier)
        self.metadata.setMetadataPair(metadata.METADATA_FULL_PACKAGENAME, self.sipPackageName)

    
    #
    # return information on the EoSip product
    #
    def info(self):
        out=StringIO()
        print >>out, "\n\n#########################################"
        print >>out, "####### START EOSIP Product Info ########"
        if self.created:
            print >>out, "# created ?                       :True #"
        else:
            print >>out, "# created ?                       :False#"

            
        if self.loaded:
            print >>out, "# loaded ?                        :True #"
            print >>out, "# loaded from:%s" % self.path
            print >>out, "#  %s" % self.loadingMessage[0:-1]
            if len(self.eoPieces)>0:
                n=0
                print >>out, "#"
                for item in self.eoPieces:
                    print >>out, "#  piece[%d]:%s" % (n, item.info())
                    n=n+1
        else:
            print >>out, "# loaded ?                        :False#"

            
        if self.workingOn:
            print >>out, "# working on ?:True                     #"
        else:
            print >>out, "# working on ?:False                    #"
        if self.workingOn:
            print >>out, "working on folder:%s" % self.workingOnFolder

            
        print >>out, " product stored as:%s" % self.src_product_stored
        print >>out, " product stored compression:%s" % self.src_product_stored_compression
        print >>out, " product stored eo compression:%s" % self.src_product_stored_eo_compression
        print >>out, "\n  eop:identifier:%s" % self.identifier

        print >>out, "  eo package extension:%s" % self.eoPackageExtension
        print >>out, "  Sip package extension:%s" % self.sipPackageExtension
        
        print >>out, "  Sip product name:%s" % self.sipProductName
        print >>out, "  Sip package name (with ext):%s" % self.sipPackageName
        print >>out, "  eo product name:%s" % self.eoProductName
        print >>out, "  eo package name (with ext):%s" % self.eoPackageName
        print >>out, "\n  source product path:%s" % self.sourceProductPath

        
        if self.created:
            print >>out, "   product tmp folder:%s\n" % self.folder
        else:
            print >>out, "   product folder:%s\n" % self.folder
        
        if len(self.sourceBrowsesPath)==0:
            print >>out, "   no sourceBrowsesPath"
        else:
            n=0
            for item in self.sourceBrowsesPath:
                print >>out, "   sourceBrowsesPath[%d]:%s" % (n, item)
                n=n+1
        if len(self.browsesInfo)==0:
            print >>out, "   no browse report"
        else:
            n=0
            for item in self.browsesInfo:
                print >>out, "   browse report info[%d]:%s" % (n, item)
                n=n+1
                
        print >>out, "\n   reportFullPath:%s" % self.reportFullPath
        print >>out, "   qualityReportFullPath:%s" % self.qualityReportFullPath
        #print >>out, "   browseFullPath:%s" % self.browseFullPath
        print >>out, "\n   sipFullPath:%s" % self.sipFullPath
        print >>out, "######## END EOSIP Product Info #########\n#########################################\n"
        return out.getvalue()



#
# a piece of EoSip archive:
# 
#
#
class EoPiece:
    
    def __init__(self, name):
        self.compressed=False
        self.name=name
        # path on local filesystem
        self.localPath=None
        self.alias=None
        self.type=None
        print "init EoPiece %s" % name

    def info(self):
        out=StringIO()
        print >>out, " name:%s" % self.name
        print >>out, " type:%s" % self.type
        print >>out, " compressed:%s" % self.compressed
        return out.getvalue()

        

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        eoSipProduct=EOSIP_Product("C:/Users/glavaux/Shared/LITE\spaceOut/to_be_modified/SP1_OPER_HRV__X__1A_19970514T100045_19970514T100054_000312_0075_0259.SIP.ZIP")
        eoSipProduct.debug=1
        eoSipProduct.loadProduct()
        print "EoSip info:\n%s" % eoSipProduct.info()
    except Exception, err:
        log.exception('Error from throws():')

