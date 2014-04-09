#
# this python script will find dimap products
#  extract them to a tmp folder if their integrity is ok
#  then build the metadata
#  and repackage the initial content in a newly create EoSIP product 
#
#
# -*- coding: cp1252 -*-
import os, sys
import logging
from logging.handlers import RotatingFileHandler
import time
import sys
import zipfile
import re
import string
import traceback
import ConfigParser
#
from esaProducts import dimap_tropforest_product
from esaProducts import eosip_product
import fileHelper
from esaProducts import metadata
from esaProducts import definitions_EoSip
import imageUtil


# set in configuration file
CONFIG_NAME=None
__config=None
INBOX=None
WORKSPACE=None
TMPSPACE=None
#
LIST_TYPE=None
LIST_BUILD='Internal'
FILES_NAMEPATTERN=None
FILES_EXTPATTERN=None

DIRS_NAMEPATTERN=None
DIRS_ISLEAF=None
DIRS_ISEMPTY=None


LIST_LIMIT=None
LIST_STARTDATE=None
LIST_STOPDATE=None
#
ENGINE_STATE=None
ENGINE=None
# var section name in configuration file
SETTING_Main='Main'
SETTING_Search='Search'
SETTING_Output='Output'
SETTING_metadataReport_usedMap='metadataReport-xml-map'
SETTING_browseReport_usedMap='browseReport-xml-map'
SETTING_MISSION_SPECIFIC='Mission-specific-values'
OUTPUT_RELATIVE_PATH_TREES='OUTPUT_RELATIVE_PATH_TREES'
DEFAULS_METADATA_LIST='METADATA_LIST'
# counter
num_total=0
num_done=0
num_error=0
list_done=[]
list_error=[]

# the eoSip final path list
FINAL_PATH_LIST=[]

# debug stuff
debug=0
# logger stuff
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
basicFormat='%(asctime)s - [%(levelname)s] : %(message)s'
formatter = logging.Formatter(basicFormat)
#
file_handler = RotatingFileHandler('ingest_dimap.log', '', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)


def my_Log(mess=None, eol=None):
        tmp="%s : %s" % (time.strftime('%Y%m%d %H:%M:%S'), mess)
        if eol!=None:
                tmp="%s\n" % tmp
        print tmp
        return tmp


def readConfig(path=None):
	global CONFIG_NAME, __config, OUTSPACE, INBOX, TMPSPACE, LIST_TYPE, LIST_BUILD, FILES_NAMEPATTERN, FILES_EXTPATTERN, DIRS_NAMEPATTERN, DIRS_ISLEAF,\
	DIRS_ISEMPTY, LIST_LIMIT, LIST_STARTDATE, LIST_STOPDATE
	
	try:
		logger.info(" reading configuration...")
		__config = ConfigParser.RawConfigParser()
		__config.optionxform=str
		__config.read(path)
		#
		CONFIG_NAME = __config.get(SETTING_Main, 'CONFIG_NAME')
		INBOX = __config.get(SETTING_Main, 'INBOX')
		TMPSPACE = __config.get(SETTING_Main, 'TMPSPACE')
		OUTSPACE = __config.get(SETTING_Main, 'OUTSPACE')
		#
		LIST_TYPE = __config.get(SETTING_Search, 'LIST_TYPE')
		if LIST_TYPE=='files':
			try:
				FILES_NAMEPATTERN = __config.get(SETTING_Search, 'FILES_NAMEPATTERN')
			except:
				pass
			try:
				FILES_EXTPATTERN = __config.get(SETTING_Search, 'FILES_EXTPATTERN')
			except:
				pass
		elif LIST_TYPE=='dirs':
			try:
				DIRS_NAMEPATTERN = __config.get(SETTING_Search, 'DIRS_NAMEPATTERN')
			except:
				pass
			try:
				DIRS_ISLEAF = __config.get(SETTING_Search, 'DIRS_ISLEAF')
			except:
				pass
			try:
				DIRS_ISEMPTY = __config.get(SETTING_Search, 'DIRS_ISEMPTY')
			except:
				pass

			
		try:
			LIST_LIMIT = __config.get(SETTING_Search, 'LIST_LIMIT')
		except:
			pass
		try:
			LIST_STARTDATE = __config.get(SETTING_Search, 'LIST_STARTDATE')
		except:
			pass
		try:
			LIST_STOPDATE = __config.get(SETTING_Search, 'LIST_STOPDATE')
		except:
			pass
		#
		#print "\n configuration:"
		logger.info("   INBOX: %s" % INBOX)
		logger.info("   WORKSPACE: %s" % WORKSPACE)
		logger.info("   OUTSPACE: %s" % OUTSPACE)
		#print "   #"

		#print "   LIST_BUILD: %s" % LIST_BUILD
		#print "   LIST_TYPE: %s" % LIST_TYPE
		#if LIST_TYPE=='files':
			#print "   FILES_NAMEPATTERN: %s" % FILES_NAMEPATTERN
			#print "   FILES_EXTPATTERN: %s" % FILES_EXTPATTERN
		#elif LIST_TYPE=='dirs':
			#print "   DIRS_NAMEPATTERN: %s" % DIRS_NAMEPATTERN
			#print "   DIRS_ISLEAF: %s" % DIRS_ISLEAF
			#print "   DIRS_ISEMPTY: %s" % DIRS_ISEMPTY	
		#print "   LIST_LIMIT: %s" % LIST_LIMIT
		#print "   LIST_STARTDATE: %s" % LIST_STARTDATE
		#print "   LIST_STOPDATE: %s" % LIST_STOPDATE
	except Exception, e:
		print " Error in reading configuration:"
		exc_type, exc_obj, exc_tb = sys.exc_info()
		traceback.print_exc(file=sys.stdout)
		raise e


def makeFolders():
        logger.info(" test TMPSPACE folder exists:%s" % TMPSPACE)
        if not os.path.exists(TMPSPACE):
                logger.info("  will make TMPSPACE folder:%s" % TMPSPACE)
                os.makedirs(TMPSPACE)
                
        logger.info(" test OUTSPACE folder exists:%s" % OUTSPACE)
        if not os.path.exists(OUTSPACE):
                logger.info("  will make OUTSPACE folder:%s" % OUTSPACE)
                os.makedirs(OUTSPACE)
                

def makeOutputFolders(metadata, basePath=None):                
        #create directory trees according to the configuration path rules
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
                logger.debug("resolved path rule[%d]:%s" % ( i, new_rulez))
                created.append(new_rulez)
                i=i+1
        return created

        
if __name__ == '__main__':
    logger.info("######################################\n######################################\n######################################\n######################################\nstarting...")

    #
    #
    #
    if len(sys.argv) > 1:
        try: 
            logger.info("will use configuration at path:%s" % sys.argv[1])
            configFile = sys.argv[1]

            isLeaf=0
            isEmpty=0
            reNamePattern = None
            reExtPattern = None
            
            try:
                #
                # read config
                #
                if not os.path.exists(configFile):
                    print " Error: configuration file not found: %s" % configFile
                    sys.exit(1)
                else:
                    readConfig(configFile)
                    logger.info(" configuration readed")

                #
                makeFolders()

                #
                # use fileHelper to find products
                #
                fileHelper=fileHelper.fileHelper()



            except Exception, e:
                print " Error 0:"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exc(file=sys.stdout)
                sys.exit(-1)

            if LIST_TYPE=='files':
                        # get list of files
                        reNamePattern = None
                        reExtPattern = None
                        if FILES_NAMEPATTERN != None:
                                reNamePattern = re.compile(FILES_NAMEPATTERN)
                        if FILES_EXTPATTERN != None:
                                reExtPattern = re.compile(FILES_EXTPATTERN)
                        logger.info(" reNamePattern:%s" % reNamePattern.pattern)
                        logger.info(" reExtPattern:%s" % reExtPattern.pattern)
                        fsList=fileHelper.list_files(INBOX, reNamePattern, reExtPattern)
            elif LIST_TYPE=='dirs':
                        reNamePattern = None
                        isLeaf=0
                        isEmpty=0
                        if DIRS_NAMEPATTERN != None:
                                reNamePattern = re.compile(DIRS_NAMEPATTERN)
                        logger.info(" reNamePattern:%s" % reNamePattern.pattern)
                        fsList=fileHelper.list_dirs(INBOX, reNamePattern, isLeaf, isEmpty)
            else:
                        raise "unreckognized LIST_TYPE:"+LIST_TYPE


            # get mission specific metadata values, taken from configuration file
            mission_metadatas={}
            missionSpecificSrc=dict(__config.items(SETTING_MISSION_SPECIFIC))
            n=0
            for key in missionSpecificSrc.keys():
                    value=missionSpecificSrc[key]
                    if debug!=0:
                            print "METADATA mission specific[%d]:%s=%s" % (n, key, value)
                    logger.debug("metadata fixed[%d]:%s=%s" % (n, key, value))
                    mission_metadatas[key]=value
                    n=n+1

            # get ouput folder tree path rules, taken from configuration file
            destFolderRulesList = __config.get(SETTING_Output, OUTPUT_RELATIVE_PATH_TREES)
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
                    if debug!=0:
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
                    if debug!=0:
                            print "BROWSE METADATA node used[%d]:%s=%s" % (n, key, value)
                    xmlMappingBrowse[key]=value
                    n=n+1


            #
            # use list of products
            #
            n=0
            eosipFolder=''
            tmpPath=''
            outPath=''
            num_all=len(fsList)
            for item in fsList:
                try:
                    n=n+1
                    num_total=num_total+1
                    logger.info("")
                    logger.info("")
                    logger.info("")
                    logger.info("")
                    logger.info("doing product[%d/%d]:%s" % ( n,num_all, item))
                    prodLog="\n\nDoing product[%d/%d]:%s" % ( n, num_all, item)

                    # create empty dimap product
                    dimapP = dimap_tropforest_product.Dimap_Tropforest_Product(item)

                    # test product integrity
                    fh = open(item, 'rb')
                    z = zipfile.ZipFile(fh)
                    ok = z.testzip()
                    if ok is not None:
                            print " Zip file is corrupt:%s" % item
                            print " First bad file in zip: %s" % ok
                            raise Exception("Zip file is corrupt:%s" % item)

                    # use/make tmp folder, extract product
                    tmpPath=TMPSPACE+"/workfolder_%d" % n
                    prodLog="%s\ntmp folder:%s\n" % (prodLog, tmpPath)
                    if not os.path.exists(tmpPath):
                            logger.info("  will make tmpPath folder:%s" % tmpPath)
                            os.makedirs(tmpPath)
                            prodLog="%stmp folder created:%s\n" % (prodLog, tmpPath)
                            
                    dimapP.extractToPath(tmpPath)
                    logger.info("dimap tiff:%s" % dimapP.TIF_FILE_NAME)
                    logger.info("dimap xml:%s" % dimapP.XML_FILE_NAME)
                    prodLog="%s\n\nproduct extracted:\n%s" % (prodLog, dimapP.toString())
                    
                    # create empty metadata
                    met=metadata.Metadata(mission_metadatas)
                    if debug!=0:
                            print "\n###  initial metadata dump:\n%s" % met.dump()

                    # fill metadata object
                    numAdded=dimapP.extractMetadata(met)
                    size=dimapP.extractProductFileSize()
                    grid_lat=dimapP.extractGridFromFile("lat")
                    grid_lon=dimapP.extractGridFromFile("lon")
                    grid_lat_norm=dimapP.extractGridFromFileNormalised("lat")
                    grid_lon_norm=dimapP.extractGridFromFileNormalised("lon")
                    met.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, size)
                    met.setMetadataPair('METADATA_WRS_LONGITUDE_GRID', grid_lon)
                    met.setMetadataPair('METADATA_WRS_LATITUDE_GRID', grid_lat)
                    met.setMetadataPair('METADATA_WRS_LONGITUDE_GRID_NORMALISED', grid_lon_norm)
                    met.setMetadataPair('METADATA_WRS_LATITUDE_GRID_NORMALISED', grid_lat_norm)                    
                    met.setMetadataPair(metadata.METADATA_FRAME, grid_lat_norm)
                    met.setMetadataPair(metadata.METADATA_TRACK, grid_lon_norm)
                    met.setMetadataPair(metadata.METADATA_GENERATION_TIME, time.strftime('%Y-%m-%dT%H:%M:%SZ'))
                    logger.debug("number of metadata added:%d" % numAdded)
                    
                    # build typecode, set stop datetime = start datetime
                    met.setMetadataPair(metadata.METADATA_STOP_DATE, met.getMetadataValue(metadata.METADATA_START_DATE))
                    met.setMetadataPair(metadata.METADATA_STOP_TIME, met.getMetadataValue(metadata.METADATA_START_TIME))
                    #
                    dimapP.refineMetadata()
                    #prodLog="%s\n\nsource dimap product metadata dump:\n%s\n" % (prodLog, met.dump())

                    # create EoSip content
                    # create a new EOSIP product, at a dummmy path at this time
                    eosipP=eosip_product.EOSIP_Product()
                    eosipP.sourceProductPath=item
                    # set product metadata
                    eosipP.setMetadata(met)
                    # set metadata xml in use mapping
                    eosipP.setXmlMappingMetadata(xmlMappingMetadata, xmlMappingBrowse)
                    prodLog="%seosip product created\n" %  prodLog

                    # build product/package names
                    eosipP.buildProductNames(definitions_EoSip.getDefinition('PRODUCT_EXT'))
                    logger.info("eosip product name built:%s" %  eosipP.productShortName)
                    prodLog="%seosip product name built:%s\n\n" %  (prodLog, eosipP.productShortName)
                    
                    
                    # make eoSip folder in tmpSpace
                    tmpEosipFolder  = tmpPath + "/" + eosipP.productShortName
                    prodLog="%stmpEosipFolder=%s\n" %  (prodLog, tmpEosipFolder)
                    if not os.path.exists(tmpEosipFolder):
                        logger.info("  will make tmpEosipFolder:%s" % tmpEosipFolder)
                        os.makedirs(tmpEosipFolder)

                    # make browse from tiff
                    # they will be only one browse
                    try:
                            browseSrcPath="%s/%s" % (tmpPath , dimapP.TIF_FILE_NAME)
                            browseExtension=definitions_EoSip.getBrowseExtension(0, definitions_EoSip.getDefinition('BROWSE_JPEG_EXT'))
                            browseDestPath="%s/%s.%s" % (tmpEosipFolder, eosipP.productShortName, browseExtension)
                            imageUtil.makeJpeg(browseSrcPath, browseDestPath, 50 )
                            eosipP.addSourceBrowse(browseDestPath, [])
                            prodLog="%sbrowse created:%s\n" %  (prodLog, browseDestPath)
                            logger.info("  browse created:%s" % browseDestPath)
                    except Exception, e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                errorMsg="Error generating browse:%s  %s\n%s" %  (exc_type, exc_obj, traceback.format_exc())
                                logger.error(errorMsg)
                                prodLog="%s%s\n" %  (prodLog, errorMsg)
                                prodLog="%s%s\n" %  (prodLog, traceback.format_exc())
                                raise e
                    
                    #
                    tmp=eosipP.buildSipReportFile()
                    prodLog="%sSip report file built:%s\n" %  (prodLog, tmp)
                    logger.info("Sip report file built:%s" %  (tmp))

                    #
                    tmp=eosipP.buildBrowsesReportFile()
                    n=0
                    for item in tmp:
                            prodLog="%sBrowse[%d] report file built:%s\n" %  (prodLog, n, tmp)
                            logger.info("Browse[%d] report file built:%s" %  (n, tmp))
                            n=n+1

                    #
                    tmp=eosipP.buildProductReportFile()
                    prodLog="%sProduct report file built:%s\n" %  (prodLog, tmp)


                    try:
                            fd1=open("%s/pretty.xml" % tmpPath, 'w')
                            fd1.write(eosipP.formatXml(eosipP.productReport))
                            fd1.flush()
                            fd1.close()
                    except Exception, e:
                            print "ERROR IN XML !!!!\n"
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            print "Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                            print "==>"
                            print eosipP.productReport
                            print "<=="


                    # create-if-needed/rename/ and set in object: browse files, sip file, original product, xml reports
                    # write into destination folder
                    eosipP.writeToFolder(OUTSPACE)
                    prodLog="%sproduct writen in folder:%s\n" %  (prodLog, OUTSPACE)
                    logger.info("product writen in folder:%s\n" %  (OUTSPACE))

                    list_done.append(item)
                    num_done=num_done+1


                    # try to write prodLod in tmp folder
                    #if debug!=0:
                    #        logger.info("Product log:\n%s" % prodLog)
                    try:
                        prodLogPath="%s/ingestion_%d.log" % (tmpPath, n)
                        fd=open(prodLogPath, 'w')
                        fd.write(prodLog)
                        fd.close()
                        #print "prodLog written in fodler:%s" % prodLogPath
                    except:
                        print "Error: problem writing prodLog in fodler:%s" % tmpPath


                    # build final eoSip path (real one)
                    # copy eoSip in first path
                    # make links in other paths
                    outputProductResolvedPath = makeOutputFolders(met, OUTSPACE)
                    if len(outputProductResolvedPath)==0:
                            raise Exception("no product resolved path")
                    else:
                            i=0
                            for item in outputProductResolvedPath:
                                logger.info("eoSip product tree path[%d] is:%s" %(i, item))
                                #os.makedirs(item)
                                i=i+1
                        

                    # print stats
                    logger.info("######################")
                    logger.info("###### Summary: ######")
                    logger.info("num total:%d" % num_total)
                    logger.info("num done:%d" % num_done)
                    logger.info("num error:%d" % num_error)
                
                    # just do one product for now
                    if n==1:
                            break


                except Exception, e:
                        num_error=num_error+1
                        list_error.append(item)
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        prodLog="%sError:%s  %s\n%s\n" %  (prodLog, exc_type, exc_obj, traceback.format_exc())
                        traceback.print_exc(file=sys.stdout)

                        # try to write prodLod in tmp folder
                        #print "\n\n\nProduct log:\n%s" % prodLog
                        try:
                                prodLogPath="%s/bad_ingestion_%d.log" % (tmpPath, n)
                                fd=open(prodLogPath, 'w')
                                fd.write(prodLog)
                                fd.close()
                                #print "prodLog written in fodler:%s" % prodLogPath
                        except:
                                print "Error: problem writing prodLog in fodler:%s" % tmpPath

                        if n==1:
                            break


            

        except Exception, e:
                print " Error"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exc(file=sys.stdout)

        # display list of failure products
        if len(list_error)>0:
                print "\n\nProducts in error:"
                n=0
                for item in list_error:
                        print " %d: %s" % (n, item)
                        n=n+1
                

    else:
        print "syntax: python ingest_dimap.py configuration_file.cfg"
        sys.exit(1)
