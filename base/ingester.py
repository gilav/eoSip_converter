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
from cStringIO import StringIO
from logging.handlers import RotatingFileHandler
import time,datetime
import sys
import zipfile
import re
import string
import traceback
import subprocess
import urllib

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# import parent
parentdir = os.path.dirname(currentdir)
print "##### eoSip converter dir:%s" % parentdir
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)

try:
    sys.path.index("%s/esaProducts" % parentdir)
except:
    sys.path.insert(0,"%s/esaProducts" % parentdir)


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
from ressources import ressourceProvider
from serviceClients import ApercuServiceClient
import sipBuilder
import infoKeeper



#
# setting variable name + default values (None in general)
#
# folders stuff
SETTING_CONFIG_NAME='CONFIG_NAME'
SETTING_CONFIG_VERSION='CONFIG_VERSION'
SETTING_INBOX='INBOX'
SETTING_OUTSPACE='OUTSPACE'
SETTING_TMPSPACE='TMPSPACE'
# config name and version
CONFIG_NAME=None
CONFIG_VERSION=None
# file find stuff
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
#
TYPOLOGY=None
# ??
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
SETTING_Ressources='Ressources'
SETTING_Services='Services'
# setting name in configuration file
SETTING_metadataReport_usedMap='metadataReport-xml-map'
SETTING_browseReport_usedMap='browseReport-xml-map'
SETTING_MISSION_SPECIFIC='Mission-specific-values'
SETTING_OUTPUT_RELATIVE_PATH_TREES='OUTPUT_RELATIVE_PATH_TREES'
SETTING_OUTPUT_SIP_PATTERN='OUTPUT_SIP_PATTERN'
SETTING_OUTPUT_EO_PATTERN='OUTPUT_EO_PATTERN'
# output stuff
OUTPUT_RELATIVE_PATH_TREES=None
OUTPUT_SIP_PATTERN=None
OUTPUT_EO_PATTERN=None
# workflow
SETTING_VERIFY_SRC_PRODUCT='VERIFY_SRC_PRODUCT'
SETTING_MAX_PRODUCTS_DONE='MAX_PRODUCTS_DONE'
SETTING_VALIDATE_XML='VALIDATE_XML'
SETTING_CREATE_INDEX='CREATE_INDEX'
SETTING_CREATE_THUMBNAIL='CREATE_THUMBNAIL'
SETTING_CREATE_SHOPCART='CREATE_SHOPCART'
SETTING_INDEX_ADDED_FIELD='INDEX_ADDED_FIELD'
SETTING_FIXED_BATCH_NAME='FIXED_BATCH_NAME'
SETTING_PRODUCT_OVERWRITE='PRODUCT_OVERWRITE'
SETTING_CREATE_BROWSE_REPORT='CREATE_BROWSE_REPORT'
SETTING_CREATE_SIP_REPORT='CREATE_SIP_REPORT'
# workflow, test stuff
SETTING_TEST_DONT_EXTRACT='TEST_DONT_EXTRACT'
SETTING_TEST_DONT_WRITE='TEST_DONT_WRITE'
SETTING_TEST_DONT_DO_BROWSE='TEST_DONT_DO_BROWSE'
# eoSip
SETTING_EOSIP_TYPOLOGY='TYPOLOGY'
SETTING_EOSIP_STORE_TYPE='STORE_TYPE'
SETTING_EOSIP_STORE_EO_COMPRESSION='STORE_EO_COMPRESSION'
SETTING_EOSIP_STORE_COMPRESSION='STORE_COMPRESSION'


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
max_product_done=-1
verify_xml=True
create_index=False
create_thumbnail=False
create_shopcart=False
create_browse_report=True
create_sip_report=True
index_added=None
fixed_batch_name=None
product_overwrite=False
test_dont_extract=False
test_dont_write=False
test_dont_do_browse=False
startJustReadConfig=False

# daemon
daemon=False


# eoSip, defaults
# eo product stored as zip
eoSip_store_type=eosip_product.SRC_PRODUCT_AS_ZIP
# don't compress eoSip zip
eoSip_store_compression=False
# but compress eo product
eoSip_store_eo_compression=True

# data provider stuff
dataProviders={}

# servies provider
servicesProvider=None

# default debug value
DEBUG=0

# fixed stuff
LOG_FOLDER="./log"
file_toBeDoneList="%s/%s" % (LOG_FOLDER, 'product_list.txt')

# convertion status var names:
CONVERSION_RESULT='CONVERSION_RESULT'
CONVERSION_ERROR='CONVERSION_ERROR'
CONVERSION_FULL_ERROR='CONVERSION_FULL_ERROR'
SUCCESS='SUCCESS'
FAILURE='FAILURE'



class Ingester():
        __metaclass__ = ABCMeta


        #
        #
        #
        def __init__(self):
            #
            print ' init base ingester'
            # set default values
            self.__config=None
            # file find stuff
            self.FILES_NAMEPATTERN=FILES_NAMEPATTERN
            self.FILES_EXTPATTERN=FILES_EXTPATTERN
            self.DIRS_NAMEPATTERN=DIRS_NAMEPATTERN
            self.DIRS_ISLEAF=DIRS_ISLEAF
            self.DIRS_ISEMPTY=DIRS_ISEMPTY
            self.LIST_LIMIT=LIST_LIMIT
            self.LIST_STARTDATE=LIST_STARTDATE
            self.LIST_STOPDATE=LIST_STOPDATE
            self.TYPOLOGY=TYPOLOGY
            # output stuff
            self.OUTPUT_RELATIVE_PATH_TREES=OUTPUT_RELATIVE_PATH_TREES
            self.OUTPUT_SIP_PATTERN=OUTPUT_SIP_PATTERN
            self.OUTPUT_EO_PATTERN=OUTPUT_EO_PATTERN
            # eoSip
            self.eoSip_store_type=eoSip_store_type
            self.eoSip_store_eo_compression = eoSip_store_eo_compression
            self.eoSip_store_compression = eoSip_store_compression
            self.FINAL_PATH_LIST=FINAL_PATH_LIST
            # workflow stuff
            self.create_index=create_index
            self.create_shopcart=create_shopcart
            self.create_thumbnail=create_thumbnail
            self.create_browse_report=create_browse_report
            self.create_sip_report=create_sip_report
            self.index_added=index_added
            self.fixed_batch_name=fixed_batch_name
            self.verify_product=verify_product
            self.verify_xml=verify_xml
            self.max_product_done=max_product_done
            self.test_dont_extract=test_dont_extract
            self.test_dont_write=test_dont_write
            self.test_dont_do_browse=test_dont_do_browse
            self.startJustReadConfig=startJustReadConfig
            # counter
            self.num=0
            self.num_total=0
            self.num_done=0
            self.num_error=0
            self.list_done=[]
            self.list_error=[]
            self.description_error=[]
            # debug
            self.debug=DEBUG
            # logger/debug stuff
            self.LOG_FOLDER=LOG_FOLDER
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.DEBUG)
            basicFormat='%(asctime)s - [%(levelname)s] : %(message)s'
            formatter = logging.Formatter(basicFormat)
            file_handler = RotatingFileHandler('ingester.log', '', 1000000, 1)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            steam_handler = logging.StreamHandler()
            steam_handler.setLevel(logging.DEBUG)
            steam_handler.setFormatter(formatter)
            self.logger.addHandler(steam_handler)
            #
            self.daemon=daemon
            #
            self.file_toBeDoneList=file_toBeDoneList
            #
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
            # data/service providers
            self.dataProviders={}
            self.servicesProvider=None
            self.apercuReporter=None
            self.ressourcesProvider=None
            # 
            self.infoKeeper = infoKeeper.infoKeeper()
            #
            self.mission_metadatas=mission_metadatas
            #


        #
        # set debug flag
        #
        def setDebug(self, b):
            self.debug=b


        #
        # return the home dir of the converter software
        #
        def getConverterHomeDir(self):
            res = "%s" % parentdir
            return res

        #
        #
        #
        def keepInfo(self, info, value):
            self.infoKeeper.addInfo(info, value)


        #
        # TODO: move it into service code 
        #
        def getValidationSchema(self, fileType=None):
            varName="SCHEMA_%s" % (fileType)

            if varName==SCHEMA_FROM_TYPOLOGY:
                if self.TYPOLOGY!=None:
                    print "TYPOLOGY:%s" % self.TYPOLOGY
                    varName="%s_%s" % (varName, self.TYPOLOGY)
                else:
                    print "TYPOLOGY is None"
            print "get schema from varName:%s" % varName
            path="%s/%s" % (self.getConverterHomeDir(), globals()[varName])
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
                if not os.path.exists(path):
                    raise Exception("cofiguration file:'%s' doesn't exists" % path)
                
                try:
                        self.logger.info("\n\n\n\n\n reading configuration...")
                        self.__config = ConfigParser.RawConfigParser()
                        self.__config.optionxform=str
                        self.__config.read(path)
                        #
                        self.CONFIG_NAME = self.__config.get(SETTING_Main, SETTING_CONFIG_NAME)
                        self.CONFIG_VERSION = self.__config.get(SETTING_Main, SETTING_CONFIG_VERSION)
                        self.INBOX = self.__config.get(SETTING_Main, SETTING_INBOX)
                        self.TMPSPACE = self.__config.get(SETTING_Main, SETTING_TMPSPACE)
                        self.OUTSPACE = self.__config.get(SETTING_Main, SETTING_OUTSPACE)
                        #
                        self.LIST_TYPE = self.__config.get(SETTING_Search, SETTING_LIST_TYPE)
                        if self.LIST_TYPE=='files':
                                try:
                                        self.FILES_NAMEPATTERN = self.__config.get(SETTING_Search, SETTING_FILES_NAMEPATTERN)
                                except:
                                        pass
                                try:
                                        self.FILES_EXTPATTERN = self.__config.get(SETTING_Search, SETTING_FILES_EXTPATTERN)
                                except:
                                        pass
                        elif self.LIST_TYPE=='dirs':
                                try:
                                        self.DIRS_NAMEPATTERN = self.__config.get(SETTING_Search, SETTING_DIRS_NAMEPATTERN)
                                except:
                                        pass
                                try:
                                        self.DIRS_ISLEAF = self.__config.get(SETTING_Search, SETTING_DIRS_ISLEAF)
                                except:
                                        pass
                                try:
                                        self.DIRS_ISEMPTY = self.__config.get(SETTING_Search, SETTING_DIRS_ISEMPTY)
                                except:
                                        pass

                                
                        try:
                                self.LIST_LIMIT = self.__config.getint(SETTING_Search, SETTING_LIST_LIMIT)
                        except:
                                pass
                        try:
                                self.LIST_STARTDATE = self.__config.get(SETTING_Search, SETTING_LIST_STARTDATE)
                        except:
                                pass
                        try:
                                self.LIST_STOPDATE = self.__config.get(SETTING_Search, SETTING_LIST_STOPDATE)
                        except:
                                pass

                        try:
                            self.OUTPUT_SIP_PATTERN = self.__config.get(SETTING_Output, SETTING_OUTPUT_SIP_PATTERN)
                        except:
                            pass

                        try:
                            self.OUTPUT_EO_PATTERN = self.__config.get(SETTING_Output, SETTING_OUTPUT_EO_PATTERN)
                        except:
                            pass

                        # if EO pattern not specified, set to SIP pattern
                        if self.OUTPUT_EO_PATTERN==None:
                            self.OUTPUT_EO_PATTERN=self.OUTPUT_SIP_PATTERN
                        # idem reverse
                        if self.OUTPUT_SIP_PATTERN==None:
                            self.OUTPUT_SIP_PATTERN=self.OUTPUT_EO_PATTERN

                        try:
                            self.OUTPUT_RELATIVE_PATH_TREES = self.__config.get(SETTING_Output, SETTING_OUTPUT_RELATIVE_PATH_TREES)
                        except:
                            pass




                        # workflow
                        try:
                            self.verify_product= self.__config.getboolean(SETTING_workflowp, SETTING_VERIFY_SRC_PRODUCT)
                        except:
                            pass
                        try:
                            self.max_product_done = self.__config.getint(SETTING_workflowp, SETTING_MAX_PRODUCTS_DONE)
                        except:
                            pass
                        try:
                            self.verify_xml = self.__config.getboolean(SETTING_workflowp, SETTING_VALIDATE_XML)
                        except:
                            pass
                        try:
                            self.create_index = self.__config.getboolean(SETTING_workflowp, SETTING_CREATE_INDEX)
                        except:
                            pass
                        try:
                            self.create_shopcart = self.__config.getboolean(SETTING_workflowp, SETTING_CREATE_SHOPCART)
                        except:
                            pass
                        try:
                            self.create_thumbnail = self.__config.getboolean(SETTING_workflowp, SETTING_CREATE_THUMBNAIL)
                        except:
                            pass
                        try:
                            self.index_added = self.__config.get(SETTING_workflowp, SETTING_INDEX_ADDED_FIELD)
                        except:
                            pass
                        try:
                            self.fixed_batch_name = self.__config.get(SETTING_workflowp, SETTING_FIXED_BATCH_NAME)
                        except:
                            pass
                        try:
                            self.product_overwrite = self.__config.getboolean(SETTING_workflowp, SETTING_PRODUCT_OVERWRITE)
                        except:
                            pass
                        try:
                            self.create_browse_report = self.__config.getboolean(SETTING_workflowp, SETTING_CREATE_BROWSE_REPORT)
                        except:
                            pass
                        
                        try:
                            self.create_sip_report= self.__config.getboolean(SETTING_workflowp, SETTING_CREATE_SIP_REPORT)
                        except:
                            pass
                        
                        try:
                            self.test_dont_extract= self.__config.getboolean(SETTING_workflowp, SETTING_TEST_DONT_EXTRACT)
                        except:
                            pass
                        try:
                            self.test_dont_write= self.__config.getboolean(SETTING_workflowp, SETTING_TEST_DONT_WRITE)
                        except:
                            pass
                        try:
                            self.test_dont_do_browse= self.__config.getboolean(SETTING_workflowp, SETTING_TEST_DONT_DO_BROWSE)
                        except:
                            pass
                        
                        # eoSip:
                        # mandatory block
                        try:
                            self.TYPOLOGY = self.__config.get(SETTING_eosip, SETTING_EOSIP_TYPOLOGY)
                            # is it supported
                            try:
                                sipBuilder.TYPOLOGY_REPRESENTATION_SUFFIX.index(self.TYPOLOGY)
                            except:
                                raise Exception("typology not supported:'%s'" % self.TYPOLOGY)
                        except Exception, e:
                            if self.TYPOLOGY==None:
                                self.TYPOLOGY = sipBuilder.TYPOLOGY_REPRESENTATION_SUFFIX[0]
                            else:
                                print " Error in reading configuration:"
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                traceback.print_exc(file=sys.stdout)
                                raise e

                        #optional
                        try:
                            self.eoSip_store_type = self.__config.get(SETTING_eosip, SETTING_EOSIP_STORE_TYPE)
                        except:
                            pass

                        try:
                            self.eoSip_store_compression = self.__config.getboolean(SETTING_eosip, SETTING_EOSIP_STORE_COMPRESSION)
                        except:
                            #self.eoSip_store_compression = false
                            pass

                        try:
                            self.eoSip_store_eo_compression = self.__config.getboolean(SETTING_eosip, SETTING_EOSIP_STORE_EO_COMPRESSION)
                        except:
                            #self.eoSip_store_eo_compression = True
                            pass



                        # dataProvider: optional
                        try:
                            dataProvidersSrc=dict(self.__config.items(SETTING_Data))
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


                        # Ressources: optional
                        try:
                            ressources=dict(self.__config.items(SETTING_Ressources))
                            n=0
                            self.ressourcesProvider=ressourceProvider.RessourceProvider()
                            for item in ressources:
                                value=ressources[item]
                                if self.debug!=0:
                                    print " ressource provider[%d]:%s==>%s" % (n,item,value)
                                self.ressourcesProvider.addRessourcePath(item, value)
                        except Exception, e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            print " Error  ressourcesProvider:%s %s" % (exc_type, exc_obj)
                            traceback.print_exc(file=sys.stdout)


                        # servicesProvider: optional
                        try:
                            serviceProvidersSrc=dict(self.__config.items(SETTING_Services))
                            if len(serviceProvidersSrc)!=0:
                                self.servicesProvider = serviceProvider.ServiceProvider(None)
                                n=0
                                for item in serviceProvidersSrc:
                                    try:
                                        value=serviceProvidersSrc[item]
                                        if self.debug!=0:
                                            print " service[%d]:%s==>%s" % (n,item,value)
                                        self.servicesProvider.addService(item, value, self)
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

                        self.checkConfigurationVersion()

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
        def starts(self, args):
            # new: use optparse package
            from optparse import OptionParser
            parser = OptionParser()
            parser.add_option("-c", "--config", dest="configFile", help="path of the configuration file")
            parser.add_option("-l", "--list", dest="productListFile", help="path of the file containg the products list")
            parser.add_option("-b", "--batch", dest="batchName", help="name of the batch job")
            parser.add_option("-i", "--batchId", dest="batchId", type="int", help="index of the batch job")
            parser.add_option("-o", "--outspace", dest="outbox", help="output folder")
            parser.add_option("-t", "--tmpspace", dest="tmpbox", help="tmp folder")
            parser.add_option("-m", "--max", dest="max", help="max product to do")
            parser.add_option("-d", "--daemon", dest="daemon", default=False, help="run in daemon mode, remotely controled")
            self.options, args = parser.parse_args(args)

            if self.options.configFile!=None:
                print "options readed:\n configuration file:%s" % self.options.configFile
            else:
                raise Exception("need at least a configuration file path as argument")
            if self.options.productListFile!=None:
                print " product list file:%s" % self.options.productListFile
            if self.options.batchName!=None:
                print " batch name:%s" % self.options.batchName
            if self.options.batchId!=None:
                print " batch id:%s" % self.options.batchId

            #
            self.readConfig(self.options.configFile)
            if self.options.batchName!=None:
                if self.options.batchId==None:
                    self.fixed_batch_name=self.options.batchName
                else:
                    self.fixed_batch_name="%s%d" % (self.options.batchName, self.options.batchId)
                print " ==> batchName overwritten by passed parameter:%s" % self.fixed_batch_name
                self.logger.info(" ==> batchName overwritten by passed parameter:%s" % self.fixed_batch_name)
            else:
                if self.options.batchId!=None:
                    self.fixed_batch_name="%s%d" % (self.fixed_batch_name, self.options.batchId)
                    print " ==> batchName overwritten by passed parameter:%s" % self.fixed_batch_name
                    self.logger.info(" ==> batchName overwritten by passed parameter:%s" % self.fixed_batch_name)

            print " ####################################### fixed_batch_name=%s" % self.fixed_batch_name
            if self.options.outbox!=None:
                self.OUTSPACE=self.options.outbox
                print " ==> OUTSPACE overwritten by passed parameter:%s" % self.OUTSPACE
                self.logger.info(" ==> OUTSPACE overwritten by passed parameter:%s" % self.OUTSPACE)

            if self.options.tmpbox!=None:
                self.TMPSPACE=self.options.tmpbox
                print " ==> TMPSPACE overwritten by passed parameter:%s" % self.TMPSPACE
                self.logger.info(" ==> TMPSPACE overwritten by passed parameter:%s" % self.TMPSPACE)

            if self.options.max!=None:
                self.max_product_done=self.options.max
                print " ==> max_product_done overwritten by passed parameter:%s" %  self.max_product_done
                self.logger.info(" ==> max_product_done overwritten by passed parameter:%s" %  self.max_product_done)

            if self.options.daemon:
                self.daemon=self.options.daemon
                print " will run in daemon mode:%s" % self.daemon
                self.logger.info(" will run in daemon mode:%s" % self.daemon)

            self.makeFolders()
            self.getMissionDefaults()

            # MOVED FROM processproducts
            if self.fixed_batch_name!=None:
                self.batchName="batch_%s_%s" % (self.CONFIG_NAME, self.fixed_batch_name)
            else:
                self.batchName="batch_%s_%s" % (self.CONFIG_NAME, formatUtils.dateNow(pattern="%m%d-%H%M%S"))

            # find and process products if not in daemon mode, of in  startJustreadConfig mode
            if self.startJustReadConfig==True:
                print " ==> run in justReadConfig mode"
                self.logger.info(" ==> run in justReadConfig mode")
                return
        
            if self.daemon:
                print " ==> run in daemon mode"
                self.logger.info(" ==> run in daemon mode")
            else:
                print " ==> run in findAndProcess mode"
                self.logger.info(" ==> run in findAndProcess mode")
                if self.options.productListFile!=None:
                    self.setProductsList(self.options.productListFile)
                else:
                    self.findProducts()

                # MOVED FROM processproducts
                # write file list of products
                fd=open(self.file_toBeDoneList, "w")
                fd.write("# total:%s\n" % len(self.productList))
                for item in self.productList:
                    fd.write("%s\n" % item)
                fd.write("# end of file")
                fd.close
                self.logger.info("\n\nlist of products to be done written in:%s\n\n" % (self.file_toBeDoneList))
                
                self.processProducts()

            

        #
        # make folder by the ingester
        #
        def makeFolders(self):
                self.logger.info(" test TMPSPACE folder exists:%s" % self.TMPSPACE)
                if not os.path.exists(self.TMPSPACE):
                        self.logger.info("  will make TMPSPACE folder:%s" % self.TMPSPACE)
                        os.makedirs(self.TMPSPACE)
                        
                self.logger.info(" test OUTSPACE folder exists:%s" % self.OUTSPACE)
                if not os.path.exists(self.OUTSPACE):
                        self.logger.info("  will make OUTSPACE folder:%s" % self.OUTSPACE)
                        os.makedirs(self.OUTSPACE)

                self.logger.info(" test log folder exists:%s" % self.LOG_FOLDER)
                if not os.path.exists(self.LOG_FOLDER):
                        self.logger.info("  will make log folder:%s" % self.LOG_FOLDER)
                        os.makedirs(self.LOG_FOLDER)


        #
        # save info in file in working folder
        #
        def saveInfo(self, filename=None, data=None):
            path="%s/%s" % (self.TMPSPACE, filename)
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
                if len(self.FINAL_PATH_LIST)==0:
                        raise Exception("FINAL_PATH_LIST is empty")
                i=0
                for rule in self.FINAL_PATH_LIST:
                        print "resolve path rule[%d/%d]:%s" % (i,len(self.FINAL_PATH_LIST), rule)
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
                # make working folder
                tmpPath=self.TMPSPACE+"/%s_workfolder_%s" % (self.batchName, processInfo.num)
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
                    if self.debug!=0:
                        self.logger.info(" product[%d]:%s" % (n,path))
                    n=n+1
            self.logger.info(" there are:%s products in list" % (len(lines)))
            self.productList=list


        #
        # find the products to be processed
        #
        def findProducts(self):
                aFileHelper=fileHelper.fileHelper()
                if self.LIST_TYPE=='files':
                        # get list of files
                        reNamePattern = None
                        reExtPattern = None
                        if self.FILES_NAMEPATTERN != None:
                                reNamePattern = re.compile(self.FILES_NAMEPATTERN)
                        if self.FILES_EXTPATTERN != None:
                                reExtPattern = re.compile(self.FILES_EXTPATTERN)
                        self.logger.info(" reNamePattern:%s" % reNamePattern.pattern)
                        self.logger.info(" reExtPattern:%s" % reExtPattern.pattern)
                        self.productList=aFileHelper.list_files(self.INBOX, reNamePattern, reExtPattern)
                elif self.LIST_TYPE=='dirs':
                        reNamePattern = None
                        isLeaf=0
                        isEmpty=0
                        if self.DIRS_NAMEPATTERN != None:
                                reNamePattern = re.compile(self.DIRS_NAMEPATTERN)
                        self.logger.info(" reNamePattern:%s" % reNamePattern.pattern)
                        self.productList=aFileHelper.list_dirs(self.INBOX, reNamePattern, isLeaf, isEmpty)
                else:
                        raise "unreckognized LIST_TYPE:"+self.LIST_TYPE


        #
        # get the mission default/fixed matadata values.
        # is defined in the configuration file
        #
        def getMissionDefaults(self):
                # get mission specific metadata values, taken from configuration file
                self.mission_metadatas={}
                missionSpecificSrc=dict(self.__config.items(SETTING_MISSION_SPECIFIC))
                n=0
                for key in missionSpecificSrc.keys():
                    value=missionSpecificSrc[key]
                    if self.debug!=0:
                            print "METADATA mission specific[%d]:%s=%s" % (n, key, value)
                    self.logger.debug("metadata fixed[%d]:%s=%s" % (n, key, value))
                    self.mission_metadatas[key]=value
                    n=n+1

                # get ouput folder tree path rules, taken from configuration file
                destFolderRulesList = self.__config.get(SETTING_Output, SETTING_OUTPUT_RELATIVE_PATH_TREES)
                n=0
                for ruleName in destFolderRulesList.split(','):
                    self.FINAL_PATH_LIST.append(ruleName)


                # get report metadata used node map, taken from configuration file
                # : is replaced replaced by _
                try:
                    self.xmlMappingMetadata={}
                    xmlMappingMetadataSrc=dict(self.__config.items(SETTING_metadataReport_usedMap))
                    n=0
                    for key in xmlMappingMetadataSrc.keys():
                        value=xmlMappingMetadataSrc[key]
                        key=key.replace('_',':')
                        if self.debug!=0:
                                print "METADATA node used[%d]:%s=%s" % (n, key, value)
                        self.xmlMappingMetadata[key]=value
                        n=n+1
                except:
                    print " WARNING: something happend when reading report used node map:"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    traceback.print_exc(file=sys.stdout)

                    
                # get report browse used node map, taken from configuration file
                # : is replaced replaced by _
                try:
                    self.xmlMappingBrowse={}
                    xmlMappingBrowseSrc=dict(self.__config.items(SETTING_browseReport_usedMap))
                    n=0
                    for key in xmlMappingBrowseSrc.keys():
                        value=xmlMappingBrowseSrc[key]
                        key=key.replace('_',':')
                        if self.debug!=0:
                                print "BROWSE METADATA node used[%d]:%s=%s" % (n, key, value)
                        self.xmlMappingBrowse[key]=value
                        n=n+1
                except:
                    print " WARNING: something happend when reading report browse used node map:"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    traceback.print_exc(file=sys.stdout)


        #
        # process just one products
        #
        def processSingleProduct(self, productPath, jobId):
                single_runStartTime=time.time()

                aProcessInfo=processInfo.processInfo()
                aProcessInfo.srcPath=productPath
                aProcessInfo.num=jobId
                self.setProcessInfo(aProcessInfo)
                
                #try:
                self.logger.info("")
                self.logger.info("")
                self.logger.info("")
                self.logger.info("")
                self.logger.info("doing single product: jobId=%s, path:%s" % (jobId, productPath))
                aProcessInfo.addLog("\n\ndoing single product: jobId=%s, path:%s" % (jobId, productPath))
                
                status={}
                try:
                        self.doOneProduct(aProcessInfo)
                        status[CONVERSION_RESULT]=SUCCESS
                except Exception, e:
                        status[CONVERSION_RESULT]=FAILURE
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        status[CONVERSION_FULL_ERROR]="Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                        status[CONVERSION_ERROR]="Error:%s  %s\n" %  (exc_type, exc_obj)
                        
                        try:
                            self.logger.error("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                            aProcessInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                        except  Exception, ee:
                            self.logger.error(" Error 0: adding log info into processInfo=%s:%s" % (aProcessInfo, ee))
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            print " ERROR 0 adding error in log:%s  %s" %  (exc_type, exc_obj)

                        # write log
                        try:
                                prodLogPath="%s/bad_convertion_%d.log" % (aProcessInfo.workFolder, self.num_error)
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

                return status

                            
        #
        # set some usefull flags in processInfo
        #
        def setProcessInfo(self, aProcessInfo):
            # 
            aProcessInfo.create_thumbnail=self.create_thumbnail
            aProcessInfo.create_index=self.create_index
            aProcessInfo.create_shopcart=self.create_shopcart
            aProcessInfo.verify_xml=self.verify_xml
            aProcessInfo.test_dont_extract=self.test_dont_extract
            aProcessInfo.test_dont_write=self.test_dont_write
            aProcessInfo.test_dont_do_browse=self.test_dont_do_browse
            aProcessInfo.infoKeeper=self.infoKeeper
            aProcessInfo.ingester=self

        
        #
        # process the list of products
        #
        def processProducts(self):
                #
                self.num=0
                self.num_total=0
                self.num_done=0
                self.num_error=0
                self.list_done=[]
                self.list_error=[]
                self.runStartTime=time.time()
                self.num_all=len(self.productList)

                # create index: use default header, + added if defined
                if self.create_index:
                    self.indexCreator=indexCreator.IndexCreator(None, self.index_added)
                    self.logger.info("will create index")

                # create shopcart:
                if self.create_shopcart:
                    self.shopcartCreator=shopcartCreator.ShopcartCreator(None, self.index_added)
                    self.logger.info("will create shopcart")

                #  create thumbnail:
                if self.create_thumbnail:
                    self.logger.info("will create thumbnail")

                self.statsUtil.start(len(self.productList))
                
                for item in self.productList:
                        aProcessInfo=processInfo.processInfo()
                        aProcessInfo.srcPath=item
                        aProcessInfo.num=self.num
                        # set some usefull flags
                        self.setProcessInfo(aProcessInfo)
                        
                        self.num=self.num+1
                        self.num_total=self.num_total+1
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("doing product[%d/%d][%s/%s]:%s" % ( self.num, self.num_all, self.num_done, self.num_error, item))
                        aProcessInfo.addLog("\n\nDoing product[%d/%d][%s/%s]:%s" % ( self.num, self.num_all, self.num_done, self.num_error, item))
                        try:
                                self.doOneProduct(aProcessInfo)

                                self.num_done=self.num_done+1
                                self.list_done.append(item+"|"+aProcessInfo.workFolder)

                                # apercu report
                                self.reportToApercu(aProcessInfo, "NAME=EoSip-converter&BINDING=converter:ingester&all=%s&done=%s&total=%s&error=%s&endTime=%s" % (self.num_all, self.num_done, self.num_total, self.num_error, urllib.quote(self.statsUtil.getEndDate())))

                                if self.create_index:
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

                                if self.create_shopcart:
                                    try:
                                        #self.shopcartCreator.debug=1
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
                                        prodLogPath="%s/conversion_%d.log" % (aProcessInfo.workFolder, self.num_error)
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
                                self.num_error=self.num_error+1
                                self.list_error.append("%s|%s" % (item,aProcessInfo.workFolder))
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                print " ERROR:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())

                                # apercu report
                                self.reportToApercu(aProcessInfo, "NAME=EoSip-converter&BINDING=converter:ingester&done=%s&total=%s&error=%s&endTime=%s" % (self.num_done, self.num_total, self.num_error, urllib.quote(self.statsUtil.getEndDate())))

                                # 
                                try:
                                    self.logger.error("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                    aProcessInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                    #print " TODO 1: aProcessInfo=%s" % aProcessInfo
                                    #print " TODO 2: aProcessInfo=%s" % dir(aProcessInfo)
                                    #aProcessInfo.addInfo("HELLO", "wefasefwaefw")
                                    #aProcessInfo.addLog("HELLO")
                                    #print " TODO 3"
                                except  Exception, ee:
                                    #self.logger.error(" Error 1: adding log info into processInfo=%s:%s" % (aProcessInfo, ee))
                                    #exc_type, exc_obj, exc_tb = sys.exc_info()
                                    #print " ERROR 1 adding error in log:%s  %s" %  (exc_type, exc_obj)
                                    pass

                                # write log
                                try:
                                        prodLogPath="%s/bad_convertion_%d.log" % (aProcessInfo.workFolder, self.num_error)
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


                        if  self.max_product_done!=-1 and self.num>= self.max_product_done:
                                self.logger.info("max number of product to be done reached:%s; STOPPING" %  self.max_product_done)
                                break


                self.runStopTime=time.time()
                tmp=self.summary()
                
                # write convertion log
                if not os.path.exists(self.LOG_FOLDER):
                    os.makedirs(self.LOG_FOLDER)
                path="%s/%s.log" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                fd.write(tmp)
                fd.close()
                print " batch done log '%s' written in:%s" % (self.batchName, path)

                # write keeped info in any
                path="%s/%s_KEEPED.txt" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                fd.write(self.infoKeeper.toString())
                fd.close()
                print " keeped information '%s' written in:%s" % (self.batchName, path)
                
                # write done list
                path="%s/%s_DONE.log" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                for item in self.list_done:
                    fd.write(item+"\n")
                fd.close()
                # write error list
                path="%s/%s_ERROR.log" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                for item in self.list_error:
                    fd.write(item+"\n")
                fd.close()
                print " batch error log '%s' written in:%s" % (self.batchName, path)
                
                if self.create_index:
                    # index text:
                    tmp=self.indexCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nINDEX:\n%s"  % tmp
                    path="%s/%s" % (self.OUTSPACE, '%s_index.txt' % self.fixed_batch_name)
                    fd=open(path, "w")
                    fd.write(tmp)
                    fd.close()
                    print "\n index written in:%s" % (path)

                if self.create_shopcart:
                    # index text:
                    tmp=self.shopcartCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nSHOPCART:\n%s"  % tmp
                    path="%s/%s" % (self.OUTSPACE, '%s_shopcart.txt' % self.fixed_batch_name)
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
            res="Summary:\nbatch name:%s\n Started at: %s" % (self.batchName, formatUtils.dateFromSec((self.runStartTime)))
            res="%s\n Stoped at: %s\n" % (res, formatUtils.dateFromSec(self.runStopTime))
            res="%s Duration: %s sec\n" % (res, (self.runStopTime-self.runStartTime))
            res="\n%s TMPSPACE:%s\n" % (res,self.TMPSPACE)
            res="\n%s OUTSPACE:%s\n" % (res,self.OUTSPACE)
            res="%s Total of products to be processed:%d\n" % (res,self.num_total)
            res="%s  Number of product done:%d\n" % (res,self.num_done)
            res="%s  Number of errors:%d\n\n" % (res,self.num_error)
            n=0
            for item in self.list_done:
                res="%s done[%d]:%s\n" % (res, n, item)
                n=n+1
            n=0
            res="%s\n" % res
            for item in self.list_error:
                res="%s errors[%d]:%s\n" % (res, n, item)
                n=n+1
            res="\n\n%s  Number of product done:%d\n" % (res,self.num_done)
            res="%s  Number of errors:%d\n" % (res,self.num_error)
            res="\n%s Duration: %s sec\n" % (res, (self.runStopTime-self.runStartTime))
            print res
            return res

 
        #
        # do one product
        #
        def doOneProduct(self, pInfo):

                startProcessing=time.time()
                # create work folder
                workfolder=self.makeWorkingFolders(pInfo)
                #
                if self.verify_product==1:
                    self.verifySourceProduct(pInfo)
                # instanciate source product
                self.createSourceProduct(pInfo)
                # make processInfo available in source product
                pInfo.srcProduct.processInfo=pInfo
                # prepare it: move/decompress it in work folder
                self.prepareProducts(pInfo)
                # create empty metadata
                met=metadata.Metadata(self.mission_metadatas)
                met.setMetadataPair(metadata.METADATA_ORIGINAL_NAME, pInfo.srcProduct.origName)
                if self.debug!=0:
                        print "\n###  initial metadata dump:\n%s" % met.toString()
                #
                self.extractMetadata(met, pInfo)
                if self.debug!=0:
                        print "\n###  final metadata dump:\n%s" % met.toString()

                # instanciate destination product
                self.createDestinationProduct(pInfo)
                # set processInfo into destination product, to make it access things like the srcProduct or ingester
                pInfo.destProduct.TYPOLOGY=self.TYPOLOGY
                pInfo.destProduct.setSrcProductStoreType(self.eoSip_store_type)
                pInfo.destProduct.setSrcProductStoreCompression(self.eoSip_store_compression)
                pInfo.destProduct.setSrcProductStoreEoCompression(self.eoSip_store_eo_compression)
                pInfo.destProduct.setProcessInfo(pInfo)
                # set the EOP typology used
                met.setOtherInfo("TYPOLOGY_SUFFIX", self.TYPOLOGY)


                # set metadata if not already defined
                if pInfo.destProduct.metadata==None: #.isMetadataDefined():
                    pInfo.destProduct.setMetadata(met)
                pInfo.destProduct.setXmlMappingMetadata(self.xmlMappingMetadata, self.xmlMappingBrowse)

                # build product name
                self.logger.info("  will build Eo-Sip package name" )
                pInfo.addLog("\n - will build Eo-Sip package name")

                #if self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_ZIP:
                #    pInfo.destProduct.buildEoNames(definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT'))
                #elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_TAR:
                #    pInfo.destProduct.buildEoNames(definitions_EoSip.getDefinition('TAR_EXT'))
                #elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_TGZ:
                #    pInfo.destProduct.buildEoNames(definitions_EoSip.getDefinition('TGZ_EXT'))
                #elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_DIR:
                #    pInfo.destProduct.buildEoNames()

                if self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_ZIP:
                    pInfo.destProduct.setEoExtension(definitions_EoSip.getDefinition('EOSIP_PRODUCT_EXT'))
                elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_TAR:
                    pInfo.destProduct.setEoExtension(definitions_EoSip.getDefinition('TAR_EXT'))
                elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_TGZ:
                    pInfo.destProduct.setEoExtension(definitions_EoSip.getDefinition('TGZ_EXT'))
                elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_DIR:
                    pInfo.destProduct.setEoExtension(None)
                elif self.eoSip_store_type==eosip_product.SRC_PRODUCT_AS_FILE:
                    pInfo.destProduct.setEoExtension(None)

                    
                pInfo.destProduct.buildEoNames()

                self.logger.info("  Sip product name (no ext):%s"  % pInfo.destProduct.sipProductName)
                pInfo.addLog("  => Sip product name (no ext):%s"  % pInfo.destProduct.sipProductName)
                self.logger.info("  Sip package name (with ext):%s"  % pInfo.destProduct.sipPackageName)
                pInfo.addLog("  => Sip package name (with ext):%s"  % pInfo.destProduct.sipPackageName)
                
                self.logger.info("  Eo product name (no ext):%s"  % pInfo.destProduct.eoProductName)
                pInfo.addLog("  => Eo product name (no ext):%s"  % pInfo.destProduct.eoProductName)
                self.logger.info("  Eo package name (with ext):%s"  % pInfo.destProduct.eoPackageName)
                pInfo.addLog("  => Eo package name (with ext):%s"  % pInfo.destProduct.eoPackageName)

                # make Eo-Sip tmp folder
                pInfo.eosipTmpFolder = pInfo.workFolder + "/" + pInfo.destProduct.sipProductName
                if not os.path.exists(pInfo.eosipTmpFolder):
                        self.logger.info("  will make tmpEosipFolder:%s" % pInfo.eosipTmpFolder)
                        pInfo.addLog("  will make tmpEosipFolder:%s" % pInfo.eosipTmpFolder)
                        os.makedirs(pInfo.eosipTmpFolder)
                #
                pInfo.destProduct.folder=pInfo.eosipTmpFolder

                # CODE MOVED FROM specialized ingested
                self.outputProductResolvedPaths = pInfo.destProduct.getOutputFolders(self.OUTSPACE, self.OUTPUT_RELATIVE_PATH_TREES)
                relativePathPart=self.outputProductResolvedPaths[0][len(self.OUTSPACE):]
                met.setMetadataPair(metadata.METADATA_PRODUCT_RELATIVE_PATH, relativePathPart)


                # make browse file
                self.makeBrowses(pInfo)

                # 
                self.beforeReportsDone(pInfo)

                # make report files
                # SIP report
                if self.create_sip_report == True:
                    pInfo.addLog("\n - will build SIP file")
                    self.logger.info("  will build SIP file")
                    tmp=pInfo.destProduct.buildSipReportFile()
                    pInfo.addLog("  => Sip report file built well:%s" %  (tmp))
                    self.logger.info("  Sip report file built well:%s" %  (tmp))


                # browse reports
                if self.create_browse_report == True:
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

                # 
                self.afterReportsDone(pInfo)

                # display some info
                print pInfo.destProduct.info()
                
                # output Eo-Sip product
                if self.test_dont_write!=True:
                    self.output_eoSip(pInfo, self.OUTSPACE, self.OUTPUT_RELATIVE_PATH_TREES, self.product_overwrite)

                # save metadata in working folder
                self.saveMetadata(pInfo)

                # 
                self.afterProductDone(pInfo)
                
                # compute stats
                #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  00"
                processingDuration=time.time()-startProcessing
                size=None
                try:
                    # TODO: move get size into product??
                    if pInfo.destProduct.path!=None:
                        size=os.stat(pInfo.destProduct.path).st_size
                    #self.logger.info("  batch run will be completed at:%s" % self.statsUtil.getEndDate())
                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  11"
                except:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    pInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                    self.logger.info("Error doing stats")
                    #pass
                #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  22"
                self.statsUtil.oneDone(processingDuration, size)
                print "\n\n\n\nLog:%s\n" % pInfo.prodLog
                print "\n\n\n\nProcess info:%s\n" % pInfo.toString()
                self.logger.info("\n####\n####\n    batch run will be completed at:%s\n####\n####" % self.statsUtil.getEndDate())
                #print "\n####\n  batch run will be completed at:%s\n####" % self.statsUtil.getEndDate()

        #
        # dump info
        #
        def dump__(self):
                self.logger.info("   INBOX: %s" % self.INBOX)
                self.logger.info("   TMPSPACE: %s" % self.TMPSPACE)
                self.logger.info("   OUTSPACE: %s" % self.OUTSPACE)
                self.logger.info("   Max product done limit: %s" % self.max_product_done)
                self.logger.info("   Verify product: %s" % self.verify_product)
                self.logger.info("   Verify xml created: %s" % self.verify_xml)
                self.logger.info("   Create thumbnail: %s" % self.create_thumbnail)
                self.logger.info("   Create index: %s" % self.create_index)
                self.logger.info("   Create shopcart: %s" % self.create_shopcart)
                self.logger.info("   Create browse report: %s" % self.create_browse_report)
                self.logger.info("   Create sip report: %s" % self.create_sip_report)
                self.logger.info("   Index added: %s" % self.index_added)
                self.logger.info("   Fixed batch name: %s" % self.fixed_batch_name)
                self.logger.info("   Product overwrite: %s" % self.product_overwrite)
                self.logger.info("   OUTPUT_SIP_PATTERN: %s" % self.OUTPUT_SIP_PATTERN)
                self.logger.info("   OUTPUT_EO_PATTERN: %s" % self.OUTPUT_EO_PATTERN)
                self.logger.info("   OUTPUT_RELATIVE_PATH_TREES: %s" % self.OUTPUT_RELATIVE_PATH_TREES)
                self.logger.info("   eoSip typology: %s" % self.TYPOLOGY)
                self.logger.info("   eoSip store type: %s" % self.eoSip_store_type)
                self.logger.info("   eoSip store compression: %s" % self.eoSip_store_compression)
                self.logger.info("   eoSip store Eo productt compression: %s" % self.eoSip_store_eo_compression)
                self.logger.info("   TEST; don't extract source product: %s" % self.test_dont_extract)
                self.logger.info("   TEST; don't write destination product: %s" % self.test_dont_write)
                self.logger.info("   TEST; don't do browse: %s" % self.test_dont_do_browse)
                #if len(dataProviders) > 0:
                self.logger.info("   additional data providers:%s" % self.dataProviders)
                #else:
                #    print "   no dataprovider"
                self.logger.info("   additional service providers:%s" % self.servicesProvider)
                #raise Exception("STOP")
                

        #
        # dump info
        #
        def dump(self):
            print self.toString()


            
        #
        # return info
        #
        def toString(self):
            out=StringIO()
            print >>out, ("   CONFIGURATION: %s" % self.CONFIG_NAME)
            print >>out, ("   CONFIG VERSION: %s" % self.CONFIG_VERSION)
            print >>out, ("   INBOX: %s" % self.INBOX)
            print >>out, ("   TMPSPACE: %s" % self.TMPSPACE)
            print >>out, ("   OUTSPACE: %s" % self.OUTSPACE)
            print >>out, ("   Max product done limit: %s" % self.max_product_done)
            print >>out, ("   Verify product: %s" % self.verify_product)
            print >>out, ("   Verify xml created: %s" % self.verify_xml)
            print >>out, ("   Create thumbnail: %s" % self.create_thumbnail)
            print >>out, ("   Create index: %s" % self.create_index)
            print >>out, ("   Create shopcart: %s" % self.create_shopcart)
            
            print >>out, ("   Create browse repor: %s" % self.create_browse_report)
            print >>out, ("   Create sip repor: %s" % self.create_sip_report)
            
            print >>out, ("   Index added: %s" % self.index_added)
            print >>out, ("   Fixed batch name: %s" % self.fixed_batch_name)
            print >>out, ("   Product overwrite: %s" % self.product_overwrite)
            print >>out, ("   OUTPUT_SIP_PATTERN: %s" % self.OUTPUT_SIP_PATTERN)
            print >>out, ("   OUTPUT_EO_PATTERN: %s" % self.OUTPUT_EO_PATTERN)
            print >>out, ("   OUTPUT_RELATIVE_PATH_TREES: %s" % self.OUTPUT_RELATIVE_PATH_TREES)
            print >>out, ("   eoSip typology: %s" % self.TYPOLOGY)
            print >>out, ("   eoSip store type: %s" % self.eoSip_store_type)
            print >>out, ("   eoSip store compression: %s" % self.eoSip_store_compression)
            print >>out, ("   eoSip store Eo productt compression: %s" % self.eoSip_store_eo_compression)
            print >>out, ("   TEST; don't extract source product: %s" % self.test_dont_extract)
            print >>out, ("   TEST; don't write destination product: %s" % self.test_dont_write)
            print >>out, ("   eoSip store type: %s" % self.eoSip_store_type)
            #if len(dataProviders) > 0:
            print >>out, ("   additional data providers:%s" % self.dataProviders)
            #else:
            #    print "   no dataprovider"
            print >>out, ("   additional service providers:%s" % self.servicesProvider)
            #
            print >>out, ("   additional ressource providers:%s" % self.ressourcesProvider)
            return out.getvalue()

                
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
                fd.write("####\n")
                fd.write(pInfo.toString())
                fd.write("\n####\n#### Process Info:\n####\n")
                fd.write(self.toString())
                fd.close()
            except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    pInfo.addLog("ERROR saving pinfo files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                    self.logger.info("ERROR saving pinfo files")
                    print"ERROR saving pinfo files:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())


        #
        #
        #
        def reportToApercu(self, pInfo, urlParams):
            try:
                # create apercu client first time
                if self.apercuReporter==None:
                    self.apercuReporter = ApercuServiceClient.ApercuServiceClient(pInfo)
                # send some name=values pairs
                self.apercuReporter.reportToApercuService(pInfo, urlParams)
            except:
                pass


        #
        # check that configuration floatVersion is >= minimum
        # config version is like: 'name_floatVersion' or 'floatVersion'
        #
        # should be abstract
        #
        #@abstractmethod
        @abstractmethod
        def checkConfigurationVersion(self, processInfo):
            raise Exception("abstractmethod")

        # implement the config version test
        def _checkConfigurationVersion(self, version, minVersion):
                pos = version.find('_')
                if pos>0:
                        version=float(version[pos+1:])
                else:
                        version=float(version)
                print "@@@@@@@@@@@@@@@@@@@@@ check version: %s %s" %  (version, minVersion)
                if version < minVersion:
                        raise Exception("Configuration version is too old; config:%s < minimum required:%s" % (version, minVersion))
                #raise Exception("abstractmethod")

        #
        # should be abstract
        #
        @abstractmethod
        def afterProductDone(self, processInfo):
                raise Exception("abstractmethod")

        #
        # should be abstract
        #
        @abstractmethod
        def beforeReportsDone(self, processInfo):
                raise Exception("abstractmethod")


        #
        # should be abstract
        #
        @abstractmethod
        def afterReportsDone(self, processInfo):
                raise Exception("abstractmethod")
                
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
