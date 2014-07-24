#
# The Ingester class is a base classe that can be used to convert Eo-Products into Eo-Sip packaged products
#
# For Esa/lite dissemination project
#
# Serco 04/2014
# Lavaux Gilles & Simone Garofalo
#
# 07/04/2014: V: 0.5
#
#
# -*- coding: cp1252 -*-

    
from abc import ABCMeta, abstractmethod
import os,sys,inspect
import logging
from logging.handlers import RotatingFileHandler
import time,datetime
import sys
import zipfile
import re
import string
import traceback

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# import parent
parentdir = os.path.dirname(currentdir)
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)

# import parent/esaProducts
try:
    sys.path.index("%s/esaProducts" % parentdir)
except:
    sys.path.insert(0,"%s/esaProducts" % parentdir)

# import parent/esaProducts/definitions_EoSip
try:
    sys.path.index("%s/esaProducts/definitions_EoSip" % parentdir)
except:
    sys.path.insert(0,"%s/esaProducts/definitions_EoSip" % parentdir) 
import ConfigParser

    
from esaProducts import eosip_product
import processInfo
import fileHelper
from esaProducts import metadata
from esaProducts import definitions_EoSip
import imageUtil
from esaProducts import formatUtils
import indexCreator, shopcartCreator
import statsUtil
from data import dataProvider
from services import serviceProvider
import sipBuilder


#
__config=None
# set in configuration file
CONFIG_NAME=None
SETTING_CONFIG_NAME='CONFIG_NAME'
INBOX=None
SETTING_INBOX='INBOX'
OUTSPACE=None
SETTING_OUTSPACE='OUTSPACE'
TMPSPACE=None
SETTING_TMPSPACE='TMPSPACE'
#
LIST_TYPE=None
SETTING_LIST_TYPE='LIST_TYPE'
LIST_BUILD='Internal'
SETTING_LIST_BUILD='LIST_BUILD'
FILES_NAMEPATTERN=None
SETTING_FILES_NAMEPATTERN='FILES_NAMEPATTERN'
FILES_EXTPATTERN=None
SETTING_FILES_EXTPATTERN='FILES_EXTPATTERN'

DIRS_NAMEPATTERN=None
SETTING_DIRS_NAMEPATTERN='DIRS_NAMEPATTERN'
DIRS_ISLEAF=None
SETTING_DIRS_ISLEAF='DIRS_ISLEAF'
DIRS_ISEMPTY=None
SETTING_DIRS_ISEMPTY='DIRS_ISEMPTY'


LIST_LIMIT=None
SETTING_LIST_LIMIT='LIST_LIMIT'
LIST_STARTDATE=None
SETTING_LIST_STARTDATE='LIST_STARTDATE'
LIST_STOPDATE=None
SETTING_LIST_STOPDATE='LIST_STOPDATE'
TYPOLOGY=None
#
ENGINE_STATE=None
SETTING_ENGINE_STATE='ENGINE_STATE'
ENGINE=None
SETTING_ENGINE='ENGINE'
#
#
# sections name in configuration file
SETTING_Main='Main'
SETTING_Search='Search'
SETTING_Output='Output'
SETTING_workflowp='Workflow'
SETTING_eosip='eoSip'
SETTING_Data='Data'
SETTING_Services='Services'
#
SETTING_metadataReport_usedMap='metadataReport-xml-map'
SETTING_browseReport_usedMap='browseReport-xml-map'
SETTING_MISSION_SPECIFIC='Mission-specific-values'
SETTING_OUTPUT_RELATIVE_PATH_TREES='OUTPUT_RELATIVE_PATH_TREES'
SETTING_OUTPUT_EO_SIP_PATTERN='OUTPUT_EO_SIP_PATTERN'
#
OUTPUT_RELATIVE_PATH_TREES=None
OUTPUT_EO_SIP_PATTERN=None
# workflow
SETTING_VERIFY_SRC_PRODUCT='VERIFY_SRC_PRODUCT'
SETTING_MAX_PRODUCTS_DONE='MAX_PRODUCTS_DONE'
SETTING_CREATE_INDEX='CREATE_INDEX'
SETTING_CREATE_THUMBNAIL='CREATE_THUMBNAIL'
SETTING_CREATE_SHOPCART='CREATE_SHOPCART'
SETTING_INDEX_ADDED_FIELD='INDEX_ADDED_FIELD'
SETTING_FIXED_BATCH_NAME='FIXED_BATCH_NAME'
SETTING_PRODUCT_OVERWRITE='PRODUCT_OVERWRITE'
# eoSip
SETTING_EOSIP_TYPOLOGY='TYPOLOGY'
SETTING_EOSIP_STORE_TYPE='STORE_TYPE'
# data provider
#SETTING_DATA_PROVIDER='provider'

#
#
# counters
num=0
num_total=0
num_done=0
num_error=0
list_done=[]
list_error=[]
description_error=[]

# the eoSip final path list
FINAL_PATH_LIST=[]

# mission stuff
mission_metadatas={}
# workflow stuff
verify_product=True
max_product_done=None
create_index=False
create_thumbnail=False
create_shopcart=False
index_added=None
fixed_batch_name=None
product_overwrite=False

# eoSip
eoSip_store_type=None

# data provider stuff
dataProviders={}

# servies provider
servicesProvider=None

# default debug value
DEBUG=0

# fixed stuff
LOG_FOLDER="./log"
file_doBeDoneList="%s/%s" % (LOG_FOLDER, 'product_list.txt')
# Eo_SIP validation schema
SCHEMA_SIP="ressources/xml_validator"
SCHEMA_BP="ressources/xml_validator/report/IF-ngEO-BrowseReport.xsd"
SCHEMA_MD_OPT="ressources/xml_validator/opt.xsd"
SCHEMA_MD_SAR="ressources/xml_validator/sar.xsd"
SCHEMA_MD_EOP="ressources/xml_validator/eop.xsd"
SCHEMA_MD_ALT="ressources/xml_validator/alt.xsd"
SCHEMA_MD_LMB="ressources/xml_validator/lmb.xsd"


class Ingester():
        __metaclass__ = ABCMeta


        #
        #
        #
        def __init__(self):
                global DEBUG
                print ' init base ingester'
                # logger stuff
                self.logger = logging.getLogger()
                self.debug=DEBUG
                self.logger.setLevel(logging.DEBUG)
                basicFormat='%(asctime)s - [%(levelname)s] : %(message)s'
                formatter = logging.Formatter(basicFormat)
                #
                file_handler = RotatingFileHandler('ingester.log', '', 1000000, 1)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                steam_handler = logging.StreamHandler()
                steam_handler.setLevel(logging.DEBUG)
                steam_handler.setFormatter(formatter)
                self.logger.addHandler(steam_handler)
                # instance vars
                self.productList=None
                #
                self.runStartTime=None
                self.runStopTime=None
                #
                self.indexCreator=None
                self.shopcartCreator=None
                self.statsUtil=statsUtil.StatsUtil()
                # resolved output folders
                self.outputProductResolvedPaths=None
                #
                self.dataProviders={}
                self.servicesProvider=None

        #
        #
        #
        def getSchema(self, fileType=None,):
            varName="SCHEMA_%s" % (fileType)
            if TYPOLOGY!=None:
                print "TYPOLOGY:%s" % TYPOLOGY
                varName="%s_%s" % (varName, TYPOLOGY)
            else:
                print "TYPOLOGY is None"
            print "get schema from varName:%s" % varName
            path="%s/%s" % (parentdir, globals()[varName])
            return path.replace('\\', '/')

        #
        # return the service provider
        #
        def getServiceProvider(self):
            return servicesProvider

        #
        # return a service by name
        #
        def getService(self, name):
            if self.servicesProvider==None:
                raise Exception("no service available")
            
            return self.servicesProvider.getService(name)

        #
        #
        #
        def readConfig(self, path=None):
                global CONFIG_NAME, __config, OUTSPACE, INBOX, TMPSPACE, LIST_TYPE, LIST_BUILD, FILES_NAMEPATTERN, FILES_EXTPATTERN, DIRS_NAMEPATTERN, DIRS_ISLEAF,\
                DIRS_ISEMPTY, LIST_LIMIT, LIST_STARTDATE, LIST_STOPDATE, OUTPUT_EO_SIP_PATTERN, OUTPUT_RELATIVE_PATH_TREES, max_product_done,\
                create_index,create_shopcart,create_thumbnail,index_added,verify_product,fixed_batch_name,product_overwrite,TYPOLOGY,eoSip_store_type #,dataProviders

                if not os.path.exists(path):
                    raise Exception("cofiguration file:'%s' doesn't exists" % path)
                
                try:
                        self.logger.info("\n\n\n\n\n reading configuration...")
                        __config = ConfigParser.RawConfigParser()
                        __config.optionxform=str
                        __config.read(path)
                        #
                        CONFIG_NAME = __config.get(SETTING_Main, SETTING_CONFIG_NAME)
                        INBOX = __config.get(SETTING_Main, SETTING_INBOX)
                        TMPSPACE = __config.get(SETTING_Main, SETTING_TMPSPACE)
                        OUTSPACE = __config.get(SETTING_Main, SETTING_OUTSPACE)
                        #
                        LIST_TYPE = __config.get(SETTING_Search, SETTING_LIST_TYPE)
                        if LIST_TYPE=='files':
                                try:
                                        FILES_NAMEPATTERN = __config.get(SETTING_Search, SETTING_FILES_NAMEPATTERN)
                                except:
                                        pass
                                try:
                                        FILES_EXTPATTERN = __config.get(SETTING_Search, SETTING_FILES_EXTPATTERN)
                                except:
                                        pass
                        elif LIST_TYPE=='dirs':
                                try:
                                        DIRS_NAMEPATTERN = __config.get(SETTING_Search, SETTING_DIRS_NAMEPATTERN)
                                except:
                                        pass
                                try:
                                        DIRS_ISLEAF = __config.get(SETTING_Search, SETTING_DIRS_ISLEAF)
                                except:
                                        pass
                                try:
                                        DIRS_ISEMPTY = __config.get(SETTING_Search, SETTING_DIRS_ISEMPTY)
                                except:
                                        pass

                                
                        try:
                                LIST_LIMIT = __config.get(SETTING_Search, SETTING_LIST_LIMIT)
                        except:
                                pass
                        try:
                                LIST_STARTDATE = __config.get(SETTING_Search, SETTING_LIST_STARTDATE)
                        except:
                                pass
                        try:
                                LIST_STOPDATE = __config.get(SETTING_Search, SETTING_LIST_STOPDATE)
                        except:
                                pass

                        try:
                            OUTPUT_EO_SIP_PATTERN = __config.get(SETTING_Output, SETTING_OUTPUT_EO_SIP_PATTERN)
                        except:
                            pass

                        try:
                            OUTPUT_RELATIVE_PATH_TREES = __config.get(SETTING_Output, SETTING_OUTPUT_RELATIVE_PATH_TREES)
                        except:
                            pass


                        # workflow
                        try:
                            verify_product= __config.getboolean(SETTING_workflowp, SETTING_VERIFY_SRC_PRODUCT)
                        except:
                            pass
                        try:
                            max_product_done = __config.get(SETTING_workflowp, SETTING_MAX_PRODUCTS_DONE)
                        except:
                            pass
                        try:
                            create_index = __config.getboolean(SETTING_workflowp, SETTING_CREATE_INDEX)
                        except:
                            pass
                        try:
                            create_shopcart = __config.getboolean(SETTING_workflowp, SETTING_CREATE_SHOPCART)
                        except:
                            pass
                        try:
                            create_thumbnail = __config.getboolean(SETTING_workflowp, SETTING_CREATE_THUMBNAIL)
                        except:
                            pass
                        try:
                            index_added = __config.get(SETTING_workflowp, SETTING_INDEX_ADDED_FIELD)
                        except:
                            pass
                        try:
                            fixed_batch_name = __config.get(SETTING_workflowp, SETTING_FIXED_BATCH_NAME)
                        except:
                            pass
                        try:
                            product_overwrite = __config.getboolean(SETTING_workflowp, SETTING_PRODUCT_OVERWRITE)
                        except:
                            pass


                        # eoSip:
                        # mandatory block
                        try:
                            TYPOLOGY = __config.get(SETTING_eosip, SETTING_EOSIP_TYPOLOGY)
                            # is it supported
                            try:
                                sipBuilder.TYPOLOGY_REPRESENTATION_SUFFIX.index(TYPOLOGY)
                            except:
                                raise Exception("typology not supported:'%s'" % TYPOLOGY)
                        except Exception, e:
                            if TYPOLOGY==None:
                                TYPOLOGY = sipBuilder.TYPOLOGY_REPRESENTATION_SUFFIX[0]
                            else:
                                print " Error in reading configuration:"
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                traceback.print_exc(file=sys.stdout)
                                raise e
                                #TYPOLOGY = sipBuilder.TYPOLOGY_REPRESENTATION_SUFFIX[0]
                                #pass

                        #optional
                        try:
                            eoSip_store_type = __config.get(SETTING_eosip, SETTING_EOSIP_STORE_TYPE)
                        except:
                            pass

                        # dataProvider: optional
                        try:
                            dataProvidersSrc=dict(__config.items(SETTING_Data))
                            n=0
                            for item in dataProvidersSrc:
                                value=dataProvidersSrc[item]
                                if self.debug!=0:
                                    print " data provider[%d]:%s==>%s" % (n,item,value)
                                aDataProvider = dataProvider.DataProvider(value)
                                self.dataProviders[item]=aDataProvider
                        except Exception, e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            print " Error  dataProvider:%s %s" % (exc_type, exc_obj)
                            traceback.print_exc(file=sys.stdout)
                            

                        # servicesProvider: optional
                        try:
                            serviceProvidersSrc=dict(__config.items(SETTING_Services))
                            if len(serviceProvidersSrc)!=0:
                                self.servicesProvider = serviceProvider.ServiceProvider(None)
                                n=0
                                for item in serviceProvidersSrc:
                                    try:
                                        value=serviceProvidersSrc[item]
                                        if self.debug!=0:
                                            print " service[%d]:%s==>%s" % (n,item,value)
                                        self.servicesProvider.addService(item, value)
                                    except:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " Error adding serviceProvider '%d':"
                                        traceback.print_exc(file=sys.stdout)
                            else:
                                print " no service provider configured"
                                        
                        except Exception, e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            print " Error  servicesProvider:%s %s" % (exc_type, exc_obj)
                            traceback.print_exc(file=sys.stdout)
                            
                        
                        self.dump()

                except Exception, e:
                        print " Error in reading configuration:"
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        traceback.print_exc(file=sys.stdout)
                        raise e

        #
        # start the ingester
        #  argv[1]: the configuration file
        #  argv[2]: the file holding the list of products
        #
        #
        # 
        def starts(self, argv):
            if len(argv) < 2:
                raise Exception("not enough parameter passed, need 1, has %d" % (len(argv)-1))
            self.readConfig(sys.argv[1])
            self.makeFolders()
            self.getMissionDefaults()
            if len(sys.argv)>2:
                self.setProductsList(sys.argv[2])
            else:
                self.findProducts()
            self.processProducts()

            
        #
        # dump info
        #
        def dump(self):
                self.logger.info("   INBOX: %s" % INBOX)
                self.logger.info("   TMPSPACE: %s" % TMPSPACE)
                self.logger.info("   OUTSPACE: %s" % OUTSPACE)
                self.logger.info("   Max product done limit: %s" % max_product_done)
                self.logger.info("   Verify product: %s" % verify_product)
                self.logger.info("   Create thumbnail: %s" % create_thumbnail)
                self.logger.info("   Create index: %s" % create_index)
                self.logger.info("   Create shopcart: %s" % create_shopcart)
                self.logger.info("   Index added: %s" % index_added)
                self.logger.info("   Fixed batch name: %s" % fixed_batch_name)
                self.logger.info("   Product overwrite: %s" % product_overwrite)
                self.logger.info("   OUTPUT_EO_SIP_PATTERN: %s" % OUTPUT_EO_SIP_PATTERN)
                self.logger.info("   OUTPUT_RELATIVE_PATH_TREES: %s" % OUTPUT_RELATIVE_PATH_TREES)
                self.logger.info("   eoSip typology: %s" % TYPOLOGY)
                self.logger.info("   eoSip store type: %s" % eoSip_store_type)
                #if len(dataProviders) > 0:
                self.logger.info("   additional data providers:%s" % self.dataProviders)
                #else:
                #    print "   no dataprovider"
                self.logger.info("   additional service providers:%s" % self.servicesProvider)
                #raise Exception("STOP")


        #
        # make folder by the ingester
        #
        def makeFolders(self):
                self.logger.info(" test TMPSPACE folder exists:%s" % TMPSPACE)
                if not os.path.exists(TMPSPACE):
                        self.logger.info("  will make TMPSPACE folder:%s" % TMPSPACE)
                        os.makedirs(TMPSPACE)
                        
                self.logger.info(" test OUTSPACE folder exists:%s" % OUTSPACE)
                if not os.path.exists(OUTSPACE):
                        self.logger.info("  will make OUTSPACE folder:%s" % OUTSPACE)
                        os.makedirs(OUTSPACE)

                self.logger.info(" test log folder exists:%s" % LOG_FOLDER)
                if not os.path.exists(LOG_FOLDER):
                        self.logger.info("  will make log folder:%s" % LOG_FOLDER)
                        os.makedirs(LOG_FOLDER)


        #
        # save info in file in working folder
        #
        def saveInfo(self, filename=None, data=None):
            path="%s/%s" % (TMPSPACE, filename)
            fd=open(path, "a+")
            fd.write(data)
            fd.write("\n")
            fd.close()
            
            

                        
        #
        # make the destination folder
        #
        def makeOutputFolders(self, metadata, basePath=None):
                #create output directory trees according to the configuration path rules
                created=[]
                if basePath[-1]!='/':
                        basePath="%s/" % basePath
                if len(FINAL_PATH_LIST)==0:
                        raise Exception("FINAL_PATH_LIST is empty")
                i=0
                for rule in FINAL_PATH_LIST:
                        print "resolve path rule[%d/%d]:%s" % (i,len(FINAL_PATH_LIST), rule)
                        toks=rule.split('/')
                        new_rulez = basePath
                        n=0
                        for tok in toks:
                                new_rulez="%s%s/" % (new_rulez, metadata.getMetadataValue(tok))
                                n=n+1
                        self.logger.debug("resolved path rule[%d]:%s" % ( i, new_rulez))
                        created.append(new_rulez)
                        i=i+1
                return created

        
        #
        # make working folder
        #
        def makeWorkingFolders(self, processInfo):
                global TMPSPACE
                # make working folder
                tmpPath=TMPSPACE+"/%s_workfolder_%s" % (self.batchName, processInfo.num)
                processInfo.addLog("\n - create working folder if needed; working folder:%s" % (tmpPath))
                if not os.path.exists(tmpPath): # create it
                    processInfo.addLog("  => don't exist, create it") 
                    self.logger.info("  will make working folder:%s" % tmpPath)
                    os.makedirs(tmpPath)
                    processInfo.addLog("  working folder created:%s\n" % (tmpPath))
                else: # already exists
                    processInfo.addLog("  => already exists") 
                    pass # TODO: 
                processInfo.workFolder=tmpPath
                return tmpPath

                
        #
        # set the list of product to be processed(
        # (this list is passed as a file path parameter to the ingester)
        #
        def setProductsList(self, filePath=None):
            self.logger.info(" set product list from file:%s" % filePath)
            fd=open(filePath, "r")
            lines=fd.readlines()
            fd.close()
            list=[]
            n=0
            for line in lines:
                if line[0]!="#":
                    path=line.replace("\\","/").replace('\n','')
                    list.append(path)
                    self.logger.info(" product[%d]:%s" % (n,path))
                    n=n+1
            self.logger.info(" there are:%s products in list" % (len(lines)))
            self.productList=list


        #
        # find the products to be processed
        #
        def findProducts(self):
                aFileHelper=fileHelper.fileHelper()
                if LIST_TYPE=='files':
                        # get list of files
                        reNamePattern = None
                        reExtPattern = None
                        if FILES_NAMEPATTERN != None:
                                reNamePattern = re.compile(FILES_NAMEPATTERN)
                        if FILES_EXTPATTERN != None:
                                reExtPattern = re.compile(FILES_EXTPATTERN)
                        self.logger.info(" reNamePattern:%s" % reNamePattern.pattern)
                        self.logger.info(" reExtPattern:%s" % reExtPattern.pattern)
                        self.productList=aFileHelper.list_files(INBOX, reNamePattern, reExtPattern)
                elif LIST_TYPE=='dirs':
                        reNamePattern = None
                        isLeaf=0
                        isEmpty=0
                        if DIRS_NAMEPATTERN != None:
                                reNamePattern = re.compile(DIRS_NAMEPATTERN)
                        self.logger.info(" reNamePattern:%s" % reNamePattern.pattern)
                        self.productList=aFileHelper.list_dirs(INBOX, reNamePattern, isLeaf, isEmpty)
                else:
                        raise "unreckognized LIST_TYPE:"+LIST_TYPE


        #
        # get the mission default/fixed matadata values.
        # is defined in the configuration file
        #
        def getMissionDefaults(self):
                global __config, xmlMappingMetadata, xmlMappingBrowse, FINAL_PATH_LIST, mission_metadatas
                # get mission specific metadata values, taken from configuration file
                mission_metadatas={}
                missionSpecificSrc=dict(__config.items(SETTING_MISSION_SPECIFIC))
                n=0
                for key in missionSpecificSrc.keys():
                    value=missionSpecificSrc[key]
                    if self.debug!=0:
                            print "METADATA mission specific[%d]:%s=%s" % (n, key, value)
                    self.logger.debug("metadata fixed[%d]:%s=%s" % (n, key, value))
                    mission_metadatas[key]=value
                    n=n+1

                # get ouput folder tree path rules, taken from configuration file
                destFolderRulesList = __config.get(SETTING_Output, SETTING_OUTPUT_RELATIVE_PATH_TREES)
                n=0
                for ruleName in destFolderRulesList.split(','):
                    FINAL_PATH_LIST.append(ruleName)


                # get report metadata used node map, taken from configuration file
                # : is replaced replaced by _
                try:
                    xmlMappingMetadata={}
                    xmlMappingMetadataSrc=dict(__config.items(SETTING_metadataReport_usedMap))
                    n=0
                    for key in xmlMappingMetadataSrc.keys():
                        value=xmlMappingMetadataSrc[key]
                        key=key.replace('_',':')
                        if self.debug!=0:
                                print "METADATA node used[%d]:%s=%s" % (n, key, value)
                        xmlMappingMetadata[key]=value
                        n=n+1
                except:
                    print " WARNING: something happend when reading report used node map:"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    traceback.print_exc(file=sys.stdout)

                    
                # get report browse used node map, taken from configuration file
                # : is replaced replaced by _
                try:
                    xmlMappingBrowse={}
                    xmlMappingBrowseSrc=dict(__config.items(SETTING_browseReport_usedMap))
                    n=0
                    for key in xmlMappingBrowseSrc.keys():
                        value=xmlMappingBrowseSrc[key]
                        key=key.replace('_',':')
                        if self.debug!=0:
                                print "BROWSE METADATA node used[%d]:%s=%s" % (n, key, value)
                        xmlMappingBrowse[key]=value
                        n=n+1
                except:
                    print " WARNING: something happend when reading report browse used node map:"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    traceback.print_exc(file=sys.stdout)


        #
        # process the products
        #
        def processProducts(self):
                global CONFIG_NAME, DEBUG, num,num_total,num_done,num_error,list_done,list_error,description_error,max_product_done,create_index,create_thumbnail,create_shopcart,index_added,fixed_batch_name
                #
                if fixed_batch_name!=None:
                    self.batchName="batch_%s_%s" % (CONFIG_NAME, fixed_batch_name)
                else:
                    self.batchName="batch_%s_%s" % (CONFIG_NAME, formatUtils.dateNow(pattern="%m%d-%H%M%S"))
                #
                num=0
                num_total=0
                num_done=0
                num_error=0
                list_done=[]
                list_error=[]
                self.runStartTime=time.time()
                num_all=len(self.productList)
    
                # write file list of products
                fd=open(file_doBeDoneList, "w")
                fd.write("# total:%s\n" % len(self.productList))
                for item in self.productList:
                    fd.write("%s\n" % item)
                fd.close
                self.logger.info("\n\nlist of products to be done written in:%s\n\n" % (file_doBeDoneList))

                # create index: use default header, + added if defined
                if create_index:
                    self.indexCreator=indexCreator.IndexCreator(None, index_added)
                    self.logger.info("will create index")

                # create shopcart:
                if create_shopcart:
                    self.shopcartCreator=shopcartCreator.ShopcartCreator(None, None)
                    self.logger.info("will create shopcart")

                #  create thumbnail:
                if create_thumbnail:
                    self.logger.info("will create thumbnail")

                self.statsUtil.start(len(self.productList))
                
                for item in self.productList:
                        aProcessInfo=processInfo.processInfo()
                        aProcessInfo.srcPath=item
                        aProcessInfo.num=num
                        # set some usefull flags
                        aProcessInfo.create_thumbnail=create_thumbnail
                        aProcessInfo.create_index=create_index
                        aProcessInfo.create_shopcart=create_shopcart
                        
                        #try:
                        num=num+1
                        num_total=num_total+1
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("doing product[%d/%d][%s/%s]:%s" % ( num, num_all, num_done, num_error, item))
                        aProcessInfo.addLog("\n\nDoing product[%d/%d][%s/%s]:%s" % ( num, num_all, num_done, num_error, item))
                        try:
                                self.doOneProduct(aProcessInfo)

                                num_done=num_done+1
                                list_done.append(item+"|"+aProcessInfo.workFolder)
                                if create_index:
                                    try:
                                        if len(aProcessInfo.destProduct.browse_metadata_dict)>0: # there is at least one browse
                                            firstBrowsePath=aProcessInfo.destProduct.browse_metadata_dict.iterkeys().next()
                                            self.indexCreator.addOneProduct(aProcessInfo.destProduct.metadata, aProcessInfo.destProduct.browse_metadata_dict[firstBrowsePath])
                                        else:
                                            self.indexCreator.addOneProduct(aProcessInfo.destProduct.metadata, None)
                                    except Exception, e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " ERROR creating index:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                        aProcessInfo.addLog("ERROR creating index:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                        self.logger.error("ERROR creating index: %s  %s" % (exc_type, exc_obj))
                                        pass

                                if create_shopcart:
                                    try:
                                        if len(aProcessInfo.destProduct.browse_metadata_dict)>0: # there is at least one browse
                                            firstBrowsePath=aProcessInfo.destProduct.browse_metadata_dict.iterkeys().next()
                                            self.shopcartCreator.addOneProduct(aProcessInfo.destProduct.metadata, aProcessInfo.destProduct.browse_metadata_dict[firstBrowsePath])
                                        else:
                                            self.shopcartCreator.addOneProduct(aProcessInfo.destProduct.metadata, None)
                                    except Exception, e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " ERROR creating shopcart:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                        aProcessInfo.addLog("ERROR creating shopcart:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                        self.logger.error("ERROR creating shopcart: %s  %s" % (exc_type, exc_obj))
                                        pass


                                # write log
                                try:
                                        prodLogPath="%s/conversion_%d.log" % (aProcessInfo.workFolder, num_error)
                                        fd=open(prodLogPath, 'w')
                                        fd.write(aProcessInfo.prodLog)
                                        fd.close()
                                except Exception, eee:
                                        print "Error: problem writing convertion log in fodler:%s" % aProcessInfo.workFolder
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())

                                # save the pinfo in workfolder
                                try:
                                    self.saveProcessInfo(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving processInfo file")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving processInfo file:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                    
                                # save the matadata file in workfolder
                                try:
                                    self.saveMetadata(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving metadata files")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving metadata files:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())



                                
                        except Exception, e:
                                num_error=num_error+1
                                list_error.append("%s|%s" % (item,aProcessInfo.workFolder))
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                
                                try:
                                    self.logger.error("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                    aProcessInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                except  Exception, ee:
                                    self.logger.error(" Error: adding log info into processInfo:%s" % aProcessInfo)
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR adding error in log:%s  %s" %  (exc_type, exc_obj)

                                # write log
                                try:
                                        prodLogPath="%s/bad_convertion_%d.log" % (aProcessInfo.workFolder, num_error)
                                        fd=open(prodLogPath, 'w')
                                        fd.write(aProcessInfo.prodLog)
                                        fd.close()
                                except Exception, eee:
                                        print "Error: problem writing convertion log in fodler:%s" % aProcessInfo.workFolder
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())


                                # save the pinfo in workfolder
                                try:
                                    self.saveProcessInfo(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving processInfo file")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving processInfo file:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                    
                                # save the matadata file in workfolder
                                try:
                                    self.saveMetadata(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving metadata files")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving metadata files:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())


                        if max_product_done!=None and num>=int(max_product_done):
                                aProcessInfo.addLog("max number of product to be done reached:%s; STOPPING" % max_product_done)
                                self.logger.info("max number of product to be done reached:%s; STOPPING" % max_product_done)
                                break


                self.runStopTime=time.time()
                tmp=self.summary()
                
                # write convertion log
                if not os.path.exists(LOG_FOLDER):
                    os.makedirs(LOG_FOLDER)
                path="%s/%s.log" % (LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                fd.write(tmp)
                fd.close()
                print " batch done log '%s' written in:%s" % (self.batchName, path)
                
                # write done list
                path="%s/%s_DONE.log" % (LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                for item in list_done:
                    fd.write(item+"\n")
                fd.close()
                path="%s/%s_ERROR.log" % (LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                for item in list_error:
                    fd.write(item+"\n")
                fd.close()
                print " batch error log '%s' written in:%s" % (self.batchName, path)
                
                if create_index:
                    # index text:
                    tmp=self.indexCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nINDEX:\n%s"  % tmp
                    path="%s/%s" % (OUTSPACE, '%s_index.txt' % fixed_batch_name)
                    fd=open(path, "w")
                    fd.write(tmp)
                    fd.close()
                    print "\n index written in:%s" % (path)

                if create_shopcart!=0:
                    # index text:
                    tmp=self.shopcartCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nSHOPCART:\n%s"  % tmp
                    path="%s/%s" % (OUTSPACE, '%s_shopcart.txt' % fixed_batch_name)
                    fd=open(path, "w")
                    fd.write("%d\n" % self.shopcartCreator.getSize())
                    #fd.write("\n")
                    fd.write(tmp)
                    fd.close()
                    print "\n shopcart written in:%s" % (path)
                

        #
        #
        #
        def summary(self):
            global num,num_total,num_done,num_error,list_done,list_error,TMPSPACE,OUTSPACE
            res="Summary:\nbatch name:%s\n Started at: %s" % (self.batchName, formatUtils.dateFromSec((self.runStartTime)))
            res="%s\n Stoped at: %s\n" % (res, formatUtils.dateFromSec(self.runStopTime))
            res="%s Duration: %s sec\n" % (res, (self.runStopTime-self.runStartTime))
            res="\n%s TMPSPACE:%s\n" % (res,TMPSPACE)
            res="\n%s OUTSPACE:%s\n" % (res,OUTSPACE)
            res="%s Total of products to be processed:%d\n" % (res,num_total)
            res="%s  Number of product done:%d\n" % (res,num_done)
            res="%s  Number of errors:%d\n\n" % (res,num_error)
            n=0
            for item in list_done:
                res="%s done[%d]:%s\n" % (res, n, item)
                n=n+1
            n=0
            res="%s\n" % res
            for item in list_error:
                res="%s errors[%d]:%s\n" % (res, n, item)
                n=n+1
            res="\n\n%s  Number of product done:%d\n" % (res,num_done)
            res="%s  Number of errors:%d\n" % (res,num_error)
            res="\n%s Duration: %s sec\n" % (res, (self.runStopTime-self.runStartTime))
            print res
            return res

 
        #
        # do one product
        #
        def doOneProduct(self, pInfo):
                global product_overwrite ,eoSip_store_type, OUTPUT_EO_SIP_PATTERN, OUTSPACE

                startProcessing=time.time()
                #
                if verify_product==1:
                    self.verifySourceProduct(pInfo)
                # create work folder
                workfolder=self.makeWorkingFolders(pInfo)
                # instanciate source product
                self.createSourceProduct(pInfo)
                # prepare it: move/decompress it in work folder
                self.prepareProducts(pInfo)
                # create empty metadata
                met=metadata.Metadata(mission_metadatas)
                met.setMetadataPair(metadata.METADATA_ORIGINAL_NAME, pInfo.srcProduct.origName)
                if self.debug!=0:
                        print "\n###  initial metadata dump:\n%s" % met.toString()
                #
                self.extractMetadata(met, pInfo)
                if self.debug!=0:
                        print "\n###  final metadata dump:\n%s" % met.toString()

                # instanciate destination product
                self.createDestinationProduct(pInfo)
                # set processInfo into destination product, to make it access things like the serProduct or ingester
                pInfo.destProduct.setProcessInfo(pInfo)
                # set the EOP typology used
                met.setOtherInfo("TYPOLOGY_SUFFIX", TYPOLOGY)


                # set metadata
                pInfo.destProduct.setMetadata(met)
                pInfo.destProduct.setXmlMappingMetadata(xmlMappingMetadata, xmlMappingBrowse)

                # build product name
                self.logger.info("  will build Eo-Sip package name" )
                pInfo.addLog("\n - will build Eo-Sip package name")
                patternName = OUTPUT_EO_SIP_PATTERN
                # get eoSip extension (.ZIP normally)
                tmpExt=definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT')
                # take care of the zip in zip ==> .SIP.ZIP filename case
                #print "EoSip class name:%s" % pInfo.destProduct.__class__.__name__
                #sys.exit()
                if pInfo.destProduct.__class__.__name__ =="EOSIP_Product" and eoSip_store_type==pInfo.destProduct.SRC_PRODUCT_AS_ZIP:
                    pInfo.destProduct.buildPackageNames(patternName, "%s.%s" % (definitions_EoSip.getDefinition('SIP'), tmpExt))
                    pInfo.destProduct.buildProductNames(patternName, tmpExt)
                else:
                    pInfo.destProduct.buildPackageNames(patternName, tmpExt)
                
                self.logger.info("  Eo-Sip package name:%s"  % pInfo.destProduct.packageName)
                pInfo.addLog("  => Eo-Sip package name:%s"  % pInfo.destProduct.packageName)
                self.logger.info("  Eo-Sip product name:%s"  % pInfo.destProduct.productName)
                pInfo.addLog("  => Eo-Sip product name:%s"  % pInfo.destProduct.productName)

                # make Eo-Sip tmp folder
                pInfo.eosipTmpFolder = pInfo.workFolder + "/" + pInfo.destProduct.packageName
                if not os.path.exists(pInfo.eosipTmpFolder):
                        self.logger.info("  will make tmpEosipFolder:%s" % pInfo.eosipTmpFolder)
                        pInfo.addLog("  will make tmpEosipFolder:%s" % pInfo.eosipTmpFolder)
                        os.makedirs(pInfo.eosipTmpFolder)
                #
                pInfo.destProduct.folder=pInfo.eosipTmpFolder

                # CODE MOVED FROM specialized ingested
                self.outputProductResolvedPaths = pInfo.destProduct.getOutputFolders(OUTSPACE, OUTPUT_RELATIVE_PATH_TREES)
                relativePathPart=self.outputProductResolvedPaths[0][len(OUTSPACE):]
                met.setMetadataPair(metadata.METADATA_PRODUCT_RELATIVE_PATH, relativePathPart)

                # make browse file
                self.makeBrowses(pInfo)

                # make report files
                # SIP report
                pInfo.addLog("\n - will build SIP file")
                self.logger.info("  will build SIP file")
                tmp=pInfo.destProduct.buildSipReportFile()
                pInfo.addLog("  => Sip report file built well:%s" %  (tmp))
                self.logger.info("  Sip report file built well:%s" %  (tmp))


                # browse reports
                pInfo.addLog("\n - will build browse reports")
                self.logger.info("  will build browse reports")
                tmp=pInfo.destProduct.buildBrowsesReportFile()
                n=0
                for item in tmp:
                    pInfo.addLog("  => browse[%d] report file built:%s\n" %  (n, item))
                    self.logger.info("  browse[%d] report file built:%s" %  (n, item))
                    n=n+1

                # metadata report
                pInfo.addLog("\n - will build product report")
                self.logger.info("  will build product report")
                tmp=pInfo.destProduct.buildProductReportFile()
                pInfo.addLog("  => Product report file built well: %s" % tmp)
                self.logger.info("  Product report file built well: %s" % tmp)

                # display some info
                print pInfo.destProduct.info()
                
                # output Eo-Sip product
                self.output_eoSip(pInfo, OUTSPACE, OUTPUT_RELATIVE_PATH_TREES, product_overwrite)

                # save metadata in working folder
                self.saveMetadata(pInfo)

                processingDuration=time.time()-startProcessing
                # compute stats
                try:
                    # TODO: move get size into product??
                    size=os.stat(pInfo.destProduct.path).st_size
                    self.statsUtil.oneDone(processingDuration, size)
                    self.logger.info("  batch run will be completed at:%s" % self.statsUtil.getEndDate())
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    pInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                    self.logger.info("Error doing stats")
                    pass
                print "\n\n\n\nLog:%s\n" % pInfo.prodLog

                print "\n\n\n\nProcess info:%s\n" % pInfo.toString()

                
        #
        # save metadata as files
        #
        def saveMetadata(self, pInfo):
            if pInfo.destProduct!=None and pInfo.destProduct.metadata!=None:
                try:
                    # save metadata in working folder
                    workfolder=pInfo.workFolder
                    fd=open("%s/metadata-product.txt" % (workfolder), 'w')
                    fd.write(pInfo.destProduct.metadata.toString())
                    fd.close()
                except Exception, e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        pInfo.addLog("ERROR saving product metadata files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                        self.logger.info("ERROR saving product metadata files")
                        print "ERROR saving product metadata files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                
            if pInfo.destProduct!=None and pInfo.destProduct.browse_metadata_dict!=None and len(pInfo.destProduct.browse_metadata_dict)>0:
                try: 
                    # also browse metadata
                    n=0
                    for item in pInfo.destProduct.browse_metadata_dict.values():
                        fd=open("%s/metadata-browse-%d.txt" % (workfolder, n), 'w')
                        fd.write(item.toString())
                        fd.close()
                except Exception, e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        pInfo.addLog("ERROR saving browse metadata files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                        self.logger.info("ERROR saving browse metadata files")
                        print "ERROR saving browse metadata files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())

        #
        # save processInfo as files
        #
        def saveProcessInfo(self, pInfo):
            try:
                # save pInfo in working folder
                workfolder=pInfo.workFolder
                fd=open("%s/processInfo.txt" % (workfolder), 'w')
                fd.write(pInfo.toString())
                fd.close()
            except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    pInfo.addLog("ERROR saving pinfo files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                    self.logger.info("ERROR saving pinfo files")
                    print"ERROR saving pinfo files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                
        #
        # should be abstract
        #
        @abstractmethod
        def createSourceProduct(self, processInfo):
                raise Exception("abstractmethod")

        #
        # should be abstract
        #
        @abstractmethod
        def createDestinationProduct(self, processInfo):
                raise Exception("abstractmethod")

        #
        # should be abstract
        #
        @abstractmethod
        def verifySourceProduct(self, processInfo):
                raise Exception("abstractmethod")

        #
        # should be abstract
        #
        @abstractmethod
        def prepareProducts(self,processInfo):
                raise Exception("abstractmethod")

        #
        # should be abstract
        #
        @abstractmethod
        def extractMetadata(self,met,processInfo):
                raise Exception("abstractmethod")
                
        #
        # should be abstract
        #
        @abstractmethod
        def makeBrowses(self,processInfo):
                raise Exception("abstractmethod")

                
        #
        # should be abstract
        #
        @abstractmethod
        def output_eoSip(self, processInfo, basePath, pathRules, overwrite):
                raise Exception("abstractmethod")
                

        #
        # should be abstract
        #
        #@abstractmethod
        #def prepareBrowseMetadata(self, processInfo):
        #        raise Exception("abstractmethod")
