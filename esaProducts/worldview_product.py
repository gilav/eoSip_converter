# -*- coding: cp1252 -*-
#
# this class represent a worldview directory product
#
#  - 
#  - 
#
#
import os, sys, inspect
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
import re
from subprocess import call,Popen, PIPE
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# import parent
parentdir = os.path.dirname(currentdir)
print "##### eoSip converter dir:%s" % parentdir
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)
import fileHelper


externalConverterCommand="/bin/sh -c \"/usr/bin/gm identify -verbose "

class Worldview_Product(Directory_Product):

    MANIFEST_SUFFIX='Masterlisting.txt'

    xmlMapping={}


    def __init__(self, path=None):
        Directory_Product.__init__(self, path)
        self.manifest_filename=None
        self.manifest_info=None
        self.mul_metadata_info=None
        self.pan_metadata_info=None
        self.pan_metadata_filename=None
        self.mul_metadata_filename=None
        self.debug=1
        print " init class Worldview_Product"


    #
    # run external command to generate the browse
    #
    def externalCall(self, src=None):
        try:
            src=src.replace("//","/")
            if debug:
                print " external gm call on:%s " % (src)
                command="%s %s\"" % (externalConverterCommand, src)
            #if debug:
            print "command:'%s'" % command
            retval = subprocess.call(command, shell=True)
            print " ######################################## external exit code:%s" % retval
            if debug:
                print "  retval:%s" % retval
            if retval!=0:
                raise Exception("Error externalMakeJpeg: subprocess exit code is not 0 but:%s" % retval)
            return True
        except Exception, e:
            print " ######################################## 3 externalCall error:%s" % e
            if showTraceback:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exc(file=sys.stdout)
            raise e

        
    #
    # called at the end of the doOneProduct, before the index/shopcart creation
    #
    def afterProductDone(self):
        pass


    #
    # verify product integrity
    #
    def verifyIntegrity(self, pinfo):
        print "################## verifyIntegrity:"

        print "################## manifest content:%s" % self.manifest_info

        currentPath=''
        self.files=[]
        for line in self.manifest_info.split('\n'):
            line=line.strip().replace('\\','/')
            
            print "\n@@LINE:%s@\n" % line
            if line.find('Directory of ')>=0:
                print " -->directory:%s" % line

                pos = line.find(':')
                if pos > 0:
                    currentPath=line[pos+1:]
                    print " -->currentPath:%s" % currentPath
                    
            elif len(line)==0 or line.find(' ')>=0 or line=='[.]' or line=='[..]' or line[0]=='[' :
                pass
            
            else:
                fileLocalPath="%s%s/%s" % (self.path, currentPath, line)
                print " ->fileLocalPath:%s" % fileLocalPath
                self.files.append(fileLocalPath)

                
        # test 1
        #self.verifyFilePresent(pinfo)

        # test 2
        self.verifyTifFiles(pinfo)
                
            
    #
    # verify product integrity
    #
    def verifyFilePresent(self, pinfo):
        print "list of files"
        for item in self.files:
            print item
            if not os.path.exists(item):
                raise Exception("file %s doas not exists" % item)
                #print "ERROR: file %s does not exists" % item


    #
    # verify product integrity
    #
    def verifyTifFiles(self, pinfo):
        print "list of tif"
        for item in self.files:
            print " test %s" % item
            if item.endswith('.TIF'):
                self.verifyTif(item)
                #if not os.path.exists(item):
                #    raise Exception("file %s doas not exists" % item)
                #    #print "ERROR: file %s does not exists" % item


    #
    # verify product integrity
    #
    def verifyTif(self, path):
        print " verify tif:%s" % path
        #self.externalCall(path)

        

    #
    # read matadata file
    #
    def getMetadataInfo(self):
        if self.pan_metadata_filename==None:
            raise Exception(" no pan_metadata_filename file")
        if self.debug!=0:
            print " pan metadata source file:%s" % self.EXTRACTED_PATH+'/'+self.pan_metadata_filename
        fd=open(self.EXTRACTED_PATH+'/'+self.pan_metadata_filename, 'r')
        pan_metadata_info=fd.read()
        fd.close()
        if self.debug!=0:
            print " extract pan metadata from:%s" % pan_metadata_info


        if self.mul_metadata_filename==None:
            raise Exception(" no pan_metadata_filename file")
        if self.debug!=0:
            print " mul metadata source file:%s" % self.EXTRACTED_PATH+'/'+self.mul_metadata_filename
        fd=open(self.EXTRACTED_PATH+'/'+self.mul_metadata_filename, 'r')
        mul_metadata_info=fd.read()
        fd.close()
        if self.debug!=0:
            print " extract mul metadata from:%s" % mul_metadata_info
            
        return pan_metadata_info, mul_metadata_info



    #
    # extract the worldview
    #
    def extractToPath(self, folder=None, dont_extract=False):
        if not os.path.exists(folder):
            raise Exception("destination fodler does not exists:%s" % folder)
        if self.debug!=0:
            print " will exttact directory product '%s' to path:%s" % (self.path, folder)


        # get and keep content list. they are full path
        aFileHelper=fileHelper.fileHelper()
        reNamePattern = re.compile(".*")
        self.contentList=aFileHelper.list_files(self.path, reNamePattern, None)

        # 
        n=0
        for name in self.contentList:
            n=n+1
            if self.debug!=0:
                print "  product file[%d]:%s" % (n, name)

            # get manifest filename and data
            if name.find(self.MANIFEST_SUFFIX)>=0:
                self.manifest_filename=name
                fd=open("%s" % (name))
                self.manifest_info=fd.read()
                fd.close()
                if self.debug!=0:
                    print "   manifest found:%s" % (name)

        self.EXTRACTED_PATH=folder



    #
    #
    #
    def buildTypeCode(self):
        pass


    #
    #
    #
    def extractMetadata(self, met=None):
        if met==None:
            raise Exception("metadate is None")

        pass


    #
    # refine the metada, should perform in order:
    # - normalise date and time
    # - set platform info
    # - build type code
    #
    def refineMetadata(self):
        
        pass

        
    #
    # extract quality: use .XML for all product type
    #
    def extractQuality(self, helper, met):
        pass


    #
    # extract the footprint posList point, ccw, lat lon
    # NOTE: Deimos products have UTM coordinates in meters
    # prepare the browse report footprint block
    #
    # use .XML for KOMPSAT and AVNIR, .met for deimos
    #
    def extractFootprint(self, helper, met):
        pass
        

    def toString(self):
        res="manifest file:%s" % self.manifest_filename
        res="%s\npan metadata info:%s" % (res, self.pan_metadata_info)
        res="%s\nmul metadata info:%s" % (res, self.mul_metadata_info)
        return res


    def dump(self):
        res="manifest file:%s" % self.manifest_filename
        res="%s\npan metadata info:%s" % (res, self.pan_metadata_info)
        res="%s\nmul metadata info:%s" % (res, self.mul_metadata_info)
        print res


