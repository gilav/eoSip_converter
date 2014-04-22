#
# The Ingester class is a base classe that can be used to convert Eo-Products into Eo-Sip packaged products
#
# For Esa/ lite dissemination project
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
parentdir = os.path.dirname(currentdir)
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)
import ConfigParser

    
from esaProducts import eosip_product
import processInfo
import fileHelper
from esaProducts import metadata
from esaProducts import definitions_EoSip
import imageUtil
from esaProducts import formatUtils
import indexCreator
import statsUtil


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
#
SETTING_metadataReport_usedMap='metadataReport-xml-map'
SETTING_browseReport_usedMap='browseReport-xml-map'
SETTING_MISSION_SPECIFIC='Mission-specific-values'
SETTING_OUTPUT_RELATIVE_PATH_TREES='OUTPUT_RELATIVE_PATH_TREES'
SETTING_OUTPUT_EO_SIP_PATTERN='OUTPUT_EO_SIP_PATTERN'
#
#
#
OUTPUT_RELATIVE_PATH_TREES=None
OUTPUT_EO_SIP_PATTERN=None

# workflow
SETTING_MAX_PRODUCTS_DONE='MAX_PRODUCTS_DONE'
SETTING_CREATE_INDEX='CREATE_INDEX'
SETTING_FIXED_BATCH_NAME='FIXED_BATCH_NAME'
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
max_product_done=None
create_index=0
fixed_batch_name=None


# default debug value
DEBUG=0

# fixed stuff
LOG_FOLDER="./log"
file_doBeDoneList="%s/%s" % (LOG_FOLDER, 'product_list.txt')


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
                self.statsUtil=statsUtil.StatsUtil()
                # resolved output folders
                self.outputProductResolvedPaths=None
                


        #
        #
        #
        def readConfig(self, path=None):
                global CONFIG_NAME, __config, OUTSPACE, INBOX, TMPSPACE, LIST_TYPE, LIST_BUILD, FILES_NAMEPATTERN, FILES_EXTPATTERN, DIRS_NAMEPATTERN, DIRS_ISLEAF,\
                DIRS_ISEMPTY, LIST_LIMIT, LIST_STARTDATE, LIST_STOPDATE, OUTPUT_EO_SIP_PATTERN, OUTPUT_RELATIVE_PATH_TREES, max_product_done,\
                create_index,fixed_batch_name

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
                            max_product_done = __config.get(SETTING_workflowp, SETTING_MAX_PRODUCTS_DONE)
                        except:
                            pass
                        try:
                            create_index = __config.get(SETTING_workflowp, SETTING_CREATE_INDEX)
                        except:
                            pass

                        try:
                            fixed_batch_name = __config.get(SETTING_workflowp, SETTING_FIXED_BATCH_NAME)
                        except:
                            pass

                        self.dump()
                except Exception, e:
                        print " Error in reading configuration:"
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        traceback.print_exc(file=sys.stdout)
                        raise e

                
        #
        #
        #
        def dump(self):
                self.logger.info("   INBOX: %s" % INBOX)
                self.logger.info("   TMPSPACE: %s" % TMPSPACE)
                self.logger.info("   OUTSPACE: %s" % OUTSPACE)
                self.logger.info("   Max product done limit: %s" % max_product_done)
                self.logger.info("   Create index: %s" % create_index)
                self.logger.info("   Fixed batch name: %s" % fixed_batch_name)
                self.logger.info("   OUTPUT_EO_SIP_PATTERN: %s" % OUTPUT_EO_SIP_PATTERN)
                self.logger.info("   OUTPUT_RELATIVE_PATH_TREES: %s" % OUTPUT_RELATIVE_PATH_TREES)
                #raise Exception("STOP")


        #
        #
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
        #
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
        #
        #
        def makeWorkingFolders(self, processInfo):
                global TMPSPACE
                # make working folder
                tmpPath=TMPSPACE+"/%s_workfolder_%s" % (self.batchName, processInfo.num)
                processInfo.addLog("  working folder:%s\n" % (tmpPath))
                if not os.path.exists(tmpPath):
                    self.logger.info("  will make working folder:%s" % tmpPath)
                    os.makedirs(tmpPath)
                    processInfo.addLog("  working folder created:%s\n" % (tmpPath))
                processInfo.workFolder=tmpPath
                
        #
        #
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
        #
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
        #
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
                xmlMappingMetadataSrc=dict(__config.items(SETTING_metadataReport_usedMap))
                xmlMappingMetadata={}
                n=0
                for key in xmlMappingMetadataSrc.keys():
                    value=xmlMappingMetadataSrc[key]
                    key=key.replace('_',':')
                    if self.debug!=0:
                            print "METADATA node used[%d]:%s=%s" % (n, key, value)
                    xmlMappingMetadata[key]=value
                    n=n+1
                # get report browse used node map, taken from configuration file
                # : is replaced replaced by _
                xmlMappingBrowseSrc=dict(__config.items(SETTING_browseReport_usedMap))
                xmlMappingBrowse={}
                n=0
                for key in xmlMappingBrowseSrc.keys():
                    value=xmlMappingBrowseSrc[key]
                    key=key.replace('_',':')
                    if self.debug!=0:
                            print "BROWSE METADATA node used[%d]:%s=%s" % (n, key, value)
                    xmlMappingBrowse[key]=value
                    n=n+1
                

        #
        #
        #
        def processProducts(self):
                global CONFIG_NAME, DEBUG, num,num_total,num_done,num_error,list_done,list_error,description_error,max_product_done,create_index,fixed_batch_name
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

                #
                if create_index!=0:
                    self.indexCreator=indexCreator.IndexCreator()
                    self.logger.info("will create index")

                self.statsUtil.start(len(self.productList))
                
                for item in self.productList:
                        aProcessInfo=processInfo.processInfo()
                        aProcessInfo.srcPath=item
                        aProcessInfo.num=num
                        #try:
                        num=num+1
                        num_total=num_total+1
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("doing product[%d/%d]:%s" % ( num, num_all, item))
                        aProcessInfo.addLog("\n\nDoing product[%d/%d]:%s" % ( num, num_all, item))
                        try:
                                self.doOneProduct(aProcessInfo)

                                num_done=num_done+1
                                list_done.append(item+"|"+aProcessInfo.workFolder)
                                if create_index!=0:
                                    try:
                                        firstBrowsePath=aProcessInfo.destProduct.browse_metadata_dict.iterkeys().next()
                                        self.indexCreator.addOneProduct(aProcessInfo.destProduct.metadata, aProcessInfo.destProduct.browse_metadata_dict[firstBrowsePath])
                                    except Exception, e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " ERROR creating index:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                        aProcessInfo.addLog("ERROR creating index:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                        self.logger.error("ERROR creating index: %s  %s" % (exc_type, exc_obj))
                                        pass
                                
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

                                try:
                                        prodLogPath="%s/bad_ingestion_%d.log" % (aProcessInfo.workFolder, num)
                                        fd=open(prodLogPath, 'w')
                                        fd.write(aProcessInfo.prodLog)
                                        fd.close()
                                except Exception, eee:
                                        print "Error: problem writing prodLog in fodler:%s" % aProcessInfo.workFolder
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())

                        if max_product_done!=None and num>=int(max_product_done):
                                aProcessInfo.addLog("max number of product to be done reached:%s; STOPPING" % max_product_done)
                                self.logger.info("max number of product to be done reached:%s; STOPPING" % max_product_done)
                                break
                        
                self.runStopTime=time.time()
                tmp=self.summary()
                # write batch log
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
                
                if create_index!=0:
                    # index text:
                    tmp=self.indexCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nINDEX:\n%s"  % tmp
                    path="%s/%s" % (OUTSPACE, 'index.txt')
                    fd=open(path, "w")
                    fd.write(tmp)
                    fd.close()
                    print "\n index written in:%s" % (path)
                

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
        #
        #
        def doOneProduct(self, pInfo):
                global OUTPUT_EO_SIP_PATTERN, OUTSPACE

                startProcessing=time.time()
                self.verifySourceProduct(pInfo)
                # create work folder
                workfolder=self.makeWorkingFolders(pInfo)
                # instanciate source product
                self.createSourceProduct(pInfo)
                # prepare it: move/decompress it in work folder
                self.prepareProducts(pInfo)
                # create empty metadata
                met=metadata.Metadata(mission_metadatas)
                if self.debug!=0:
                        print "\n###  initial metadata dump:\n%s" % met.toString()
                #
                self.extractMetadata(met, pInfo)
                if self.debug!=0:
                        print "\n###  final metadata dump:\n%s" % met.toString()

                # instanciate destination product
                self.createDestinationProduct(pInfo)

                # set metadata
                pInfo.destProduct.setMetadata(met)
                pInfo.destProduct.setXmlMappingMetadata(xmlMappingMetadata, xmlMappingBrowse)

                # build product name
                patternName = OUTPUT_EO_SIP_PATTERN
                pInfo.destProduct.buildProductNames(patternName, definitions_EoSip.getDefinition('PRODUCT_EXT'))
                self.logger.info("  Eo-Sip product name:%s"  % pInfo.destProduct.productShortName)
                pInfo.addLog("  Eo-Sip product name:%s"  % pInfo.destProduct.productShortName)

                # make Eo-Sip tmp folder
                pInfo.eosipTmpFolder = pInfo.workFolder + "/" + pInfo.destProduct.productShortName
                if not os.path.exists(pInfo.eosipTmpFolder):
                        self.logger.info("  will make tmpEosipFolder:%s" % pInfo.eosipTmpFolder)
                        pInfo.addLog("  will make tmpEosipFolder:%s" % pInfo.eosipTmpFolder)
                        os.makedirs(pInfo.eosipTmpFolder)

                # CODE MOVED FROM specialized ingested
                self.outputProductResolvedPaths = pInfo.destProduct.getOutputFolders(OUTSPACE, OUTPUT_RELATIVE_PATH_TREES)
                relativePathPart=self.outputProductResolvedPaths[0][len(OUTSPACE):]
                met.setMetadataPair(metadata.METADATA_PRODUCT_RELATIVE_PATH, relativePathPart)

                # make browse file
                self.makeBrowses(pInfo)

                # make report files
                # SIP report
                tmp=pInfo.destProduct.buildSipReportFile()
                pInfo.addLog("  Sip report file built:%s" %  (tmp))
                self.logger.info("  Sip report file built:%s" %  (tmp))

                # browse reports
                tmp=pInfo.destProduct.buildBrowsesReportFile()
                n=0
                for item in tmp:
                    pInfo.addLog("  Browse[%d] report file built:%s\n" %  (n, item))
                    self.logger.info("  Browse[%d] report file built:%s" %  (n, item))
                    n=n+1

                # metadata report
                tmp=pInfo.destProduct.buildProductReportFile()
                pInfo.addLog("  Product report file built:%s" % tmp)
                self.logger.info("  Product report file built:%s" % tmp)

                #
                pInfo.destProduct.info()
                
                # output Eo-Sip product
                self.output_eoSip(pInfo, OUTSPACE, OUTPUT_RELATIVE_PATH_TREES)

                processingDuration=time.time()-startProcessing
                # compute stats
                try:
                    # TODO: move get size into product??
                    size=os.stat(pInfo.destProduct.path).st_size
                    self.statsUtil.oneDone(processingDuration, size)
                    self.logger.info("  batch run will be completed at:%s" % self.statsUtil.getEndDate())
                except:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    pInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                    self.logger.info("Error doing stats")
                    pass
                print "\n\n\n\nLog:%s\n" % pInfo.prodLog
                
                
        #
        # should be abstract
        #
        @abstractmethod
        def createSourceProduct(self, processInfo):
                processInfo.addLog("create src product")
                self.logger.info("create srcproduct")

        #
        # should be abstract
        #
        @abstractmethod
        def createDestinationProduct(self, processInfo):
                processInfo.addLog("create dest product")
                self.logger.info("create dest product") 

        #
        # should be abstract
        #
        @abstractmethod
        def verifySourceProduct(self, processInfo):
                global debug,logger
                processInfo.addLog("verifying product:%s" % (processInfo.srcPath))
                self.logger.info("verifying product");

        #
        # should be abstract
        #
        @abstractmethod
        def prepareProducts(self,processInfo):
                global debug,logger
                processInfo.addLog("prepare product in:%s" % (processInfo.workFolder))
                self.logger.info("prepare product");

        #
        # should be abstract
        #
        @abstractmethod
        def extractMetadata(self,met,processInfo):
                global debug,logger
                processInfo.addLog("extract metadata")
                self.logger.info("extract metadata")
                
        #
        # should be abstract
        #
        @abstractmethod
        def makeBrowses(self,processInfo):
                global debug,logger
                processInfo.addLog("make browses")
                self.logger.info("make browses")

                
        #
        # should be abstract
        #
        @abstractmethod
        def output_eoSip(self, processInfo, basePath, pathRules):
                global debug,logger
                processInfo.addLog("write EoSip, base path:%s" % path)
                self.logger.info("write EoSip, base path:%s" % path)
                

if __name__ == '__main__':
    print "start"
    if len(sys.argv) > 1:
            configFile = sys.argv[1]
            listOfProductFile=None
            if len(sys.argv[1])>2:
                listOfProductFile=sys.argv[2]
            ing=Ingester()
            ing.readConfig(configFile)
            ing.findProducts()
    else:
        print "syntax: python ingester.py configuration_file.cfg"
        sys.exit(1)
