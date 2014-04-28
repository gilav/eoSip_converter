# -*- coding: cp1252 -*-
#
# this class represent a EoSIP product (ZIP directory product)
#  it contains:
#  - a product 
#  - a product metadata report file
#  - zero or more browse image
#  - zero or more browse metadata report
#  - a sip volume description
#
#  it use:
#  - one metadata object for the product metadata
#  - one browse_metadata object for each browse metadata
#
# This class will create a eo-sip product(not read it at this time)
#
#
import os, sys
import logging
import zipfile
import traceback
from product import Product
from directory_product import Directory_Product
from namingConvention import NamingConvention
import definitions_EoSip
import xmlHelper
import browse_metadata, metadata
from definitions_EoSip import rep_metadataReport, rep_browseReport, SIPInfo



class EOSIP_Product(Directory_Product):
    # browse matadata dictionnary: key=browsePath, value=browse_metadata object
    browse_metadata_dict=None
    # xml node used mapping
    xmlMappingBrowse=None
    xmlMappingMetadata=None
    # xml tag that have to be replaced
    # BROWSE_CHOICE is in browse report
    # LOCAL_ATTR is in metadata report
    NODES_AS_TEXT_BLOCK=["<BROWSE_CHOICE></BROWSE_CHOICE>","<LOCAL_ATTR></LOCAL_ATTR>"]
    # default replace text, if None it can not be defaulted.
    NODES_AS_TEXT_BLOCK_DEFAULT=[None,""]


    #
    #
    #
    def __init__(self, p=None):
        Directory_Product.__init__(self, p)
        if self.debug!=0:
            print " init class EOSIP_Product, path=%s" % p
        #
        self.browse_metadata_dict={}
        #
        if p!=None:
            self.path=p
        #
        #
        self.type=Product.TYPE_EOSIP
        self.sourceBrowsesPath=[]
        #
        # the browse shortName (as in final eoSip product)
        self.browses=[]
        # and source full path
        self.sourceBrowsesPath=[]
        #
        # browse report info
        self.browsesReportInfo=[]
        # sip report
        self.sipReport=None
        # the product name (as in final eoSip product): productShortName + ext
        self.productName=None
        # the product name (as in final eoSip product)
        self.productShortName=None
        # the source of the product
        self.sourceProductPath=None
        # the product report info
        self.productReport=None
        # the browse report info
        self.browsesReport=None
        # the package name 
        self.packageName=None
        # the package extention
        self.extension=None
        #
        #
        self.sipCreator=None
        #
        self.productReportName=None
        self.reportFullPath=None
        self.browseFullPath=None
        self.sipFullPath=None

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
    def getMetadataInfo(self):
        pass

    #
    # add a source browse, create the corresponding report info
    #
    def addSourceBrowse(self, path=None, reportDict=None):
        if self.debug!=0:
            print "#############$$$$$$$$$$$$$$$ add source browse file[%d]:%s" % (len(self.sourceBrowsesPath), path)
            print "#############$$$$$$$$$$$$$$$ add source browse report[%d]:%s" % (len(self.browsesReportInfo), reportDict)
        self.browseFullPath=[]
        self.sourceBrowsesPath.append(path)
        self.browsesReportInfo.append(reportDict)
        shortName=os.path.split(path)[1]
        # create browse metadata info
        bMet=browse_metadata.Browse_Metadata()
        # set xml node used map
        bMet.xmlNodeUsedMapping=self.xmlMappingBrowse

        
        bMet.setMetadataPair(browse_metadata.BROWSE_METADATA_FILENAME, shortName)
        pos=shortName.rfind('.')
        tmp=shortName
        if pos >=0:
            tmp=tmp[0:pos]
        bMet.setMetadataPair(browse_metadata.BROWSE_METADATA_NAME, tmp)
        bMet.setMetadataPair(metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER, self.metadata.getMetadataValue(metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER))
        bMet.setMetadataPair(metadata.METADATA_START_DATE, self.metadata.getMetadataValue(metadata.METADATA_START_DATE))
        bMet.setMetadataPair(metadata.METADATA_START_TIME, self.metadata.getMetadataValue(metadata.METADATA_START_TIME))
        bMet.setMetadataPair(metadata.METADATA_STOP_DATE, self.metadata.getMetadataValue(metadata.METADATA_STOP_DATE))
        bMet.setMetadataPair(metadata.METADATA_STOP_TIME, self.metadata.getMetadataValue(metadata.METADATA_STOP_TIME))
        #
        bMet.setMetadataPair('METADATA_GENERATION_TIME', self.metadata.getMetadataValue(metadata.METADATA_GENERATION_TIME))
        bMet.setMetadataPair('METADATA_RESPONSIBLE', self.metadata.getMetadataValue('METADATA_RESPONSIBLE'))
        bMet.setMetadataPair('BROWSE_METADATA_IMAGE_TYPE', self.metadata.getMetadataValue('BROWSE_METADATA_IMAGE_TYPE'))
        self.browse_metadata_dict[path]=bMet
        


    #
    # build product and package name
    #
    def buildProductNames(self, pattern=None, ext=None ):
        self.extension=ext
        if self.debug==0:
            print " build products names, pattern=%s,ext=%s" % (pattern, ext) # using metadata:\n%s" % self.metadata.dump()
        naming = NamingConvention(pattern)
        self.productName=naming.buildProductName(self.metadata, ext)
        self.productShortName=self.productName.split('.')[0]
        self.metadata.setMetadataPair(metadata.METADATA_PRODUCTNAME, self.productShortName)

        #
        self.buildackageName()


    #
    # build the product metadata report, running the class rep_metadataReport
    #
    def buildProductReportFile(self):
        if self.debug==0:
            print "\n build product metadata report"
            print " Eo-Sip metadata dump:\n%s" % self.metadata.toString()

        # make the report xml data
        productReportBuilder=rep_metadataReport.rep_metadataReport()
        self.metadata.debug=1
        xmldata=productReportBuilder.buildMessage(self.metadata, "rep:metadataReport")

        # add the local attributes
        attr=self.metadata.getLocalAttribute()
        print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ length localattributes:%s" % len(attr)
        if len(attr) > 0:
            n=0
            res="<eop:vendorSpecific>"
            for adict in attr:
                key=adict.keys()[0]
                value=adict[key]
                print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ localattributes[%d]: %s=%s" % (n, key, value)
                res = "%s<eop:SpecificInformation><eop:localAttribute>%s</eop:localAttribute><eop:localValue>%s</eop:localValue></eop:SpecificInformation>" % (res, key, value)
                    
                n=n+1
            res="%s</eop:vendorSpecific>" % res
            print " @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ localattributes block:%s" % res
            pos = xmldata.find("<LOCAL_ATTR></LOCAL_ATTR>")
            if pos >= 0:
                xmldata=xmldata.replace("<LOCAL_ATTR></LOCAL_ATTR>", res)
            else:
                print " @@@@@@@@@@@@@@@@@@@@@@@@@ !!!!!!!!!!!!!!!!!!! no <LOCAL_ATTR></LOCAL_ATTR> block found"
            
        
        
        # verify xml, build file name
        self.productReport=self.formatXml(xmldata, self.folder, 'product_report')
        if self.debug!=0:
            print " product report content:\n%s" % self.productReport
        ext=definitions_EoSip.getDefinition("XML_EXT")
        reportName="%s.%s" % (self.productShortName, ext)
        if self.debug!=0:
            print "   product report name:%s" % (reportName)

        # sanitize test
        self.productReport=self.sanitizeXml(self.productReport)
            
        # write it
        self.reportFullPath="%s/%s" % (self.folder,reportName)
        fd=open(self.reportFullPath, "w")
        fd.write(self.productReport)
        fd.close()
        if self.debug!=0:
            print "   product report written at path:%s" % self.reportFullPath
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
        #reportFolderName=os.path.split(self.sourceBrowsesPath[0])[0]
        
        n=0
        browseReport=None
        browseReportName=None
        allBrowseReportNames=[]
        i=0
        for browsePath in self.sourceBrowsesPath:
            bmet=self.browse_metadata_dict[browsePath]
            if self.debug!=0:
                print " build browse metadata report[%d]:%s\n%s" % (n, browsePath, bmet.toString())
            #
            
            browseReportName="%s.%s" % (bmet.getMetadataValue(browse_metadata.BROWSE_METADATA_NAME), definitions_EoSip.getDefinition('XML_EXT'))
            bmet.setMetadataPair(browse_metadata.BROWSE_METADATA_REPORT_NAME, browseReportName)
            allBrowseReportNames.append(browseReportName)
            if self.debug!=0:
                print "  browse metadata report[%d] name:%s" % (n, browseReportName)
                
            browseReportBuilder=rep_browseReport.rep_browseReport()
            #browseReportBuilder.debug=1
            browseReport=self.formatXml(browseReportBuilder.buildMessage(bmet, "rep:browseReport"), self.folder, 'browse_report_%d' % i)
            # add BROWSE_CHOICE block
            browseReport=browseReport.replace('<BROWSE_CHOICE></BROWSE_CHOICE>', bmet.getMetadataValue(browse_metadata.METADATA_BROWSE_CHOICE))
            if self.debug!=0:
                print " browse report content:\n%s" % browseReport

            #
            browseReport=self.sanitizeXml(browseReport)
            
            #
            # write it
            browseFullPath="%s/%s" % (self.folder, browseReportName)
            self.browseFullPath.append(browseFullPath)
            #print " browse report content:\n%s" % browseReport
            fd=open(browseFullPath, "w")
            fd.write(browseReport)
            fd.close()
            if self.debug!=0:
                print "   browse report written at path:%s" % self.browseFullPath
            i=i+1
                
        return allBrowseReportNames


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
        sipName="%s.%s" % (self.productShortName, ext)
        if self.debug!=0:
            print "   sip report name:%s" % (sipName)

        #
        self.sipReport=self.sanitizeXml(self.sipReport)
            
        # write it
        self.sipFullPath="%s/%s" % (self.folder, sipName)
        fd=open(self.sipFullPath, "w")
        fd.write(self.sipReport)
        fd.close()
        if self.debug!=0:
            print "   sip report written at path:%s" % self.sipFullPath
        return self.sipFullPath
        
        

    #
    # build package name
    #
    def buildackageName(self):
        self.packageName=self.productName.replace(".%s"% self.extension, ".%s" % definitions_EoSip.getDefinition('PACKAGE_EXT'))
        self.metadata.setMetadataPair(metadata.METADATA_PACKAGENAME, self.packageName)

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
    # wtite the Eo-Sip product in a folder.
    #
    def writeToFolder(self, p=None):
        if self.packageName==None:
            raise Exception("Eo-Sip product has no package name")
        if self.debug==0:
            print "\n will write EoSip product at folder path:%s" % p
        if p[-1]!='/':
            p=p+'/'
        self.path="%s%s" % (p, self.packageName)
        if self.debug==0:
            print " full eoSip path:%s" % self.path

        # create folder neeedd
        if not os.path.exists(p):
            os.makedirs(p)

        # remove precedent zip if any
        if os.path.exists(self.path):
            os.remove(self.path)
        
        # create zip
        zipf = zipfile.ZipFile(self.path, 'w')
        # write product
        if self.debug!=0:
            print "  write EoSip content[0]; product itself:%s  as:%s" % (self.sourceProductPath, self.productName)
        zipf.write(self.sourceProductPath, self.productName)

        # write browses images + reports
        for browsePath in self.sourceBrowsesPath:
            folder=os.path.split(browsePath)[0]
            bmet=self.browse_metadata_dict[browsePath]
            name= "%s.%s" % (self.productShortName, definitions_EoSip.getDefinition('BROWSE_JPEG_EXT'))
            if self.debug==0:
                print "   write EoSip content[1]; product browse:%s  as:%s" % (browsePath, name)                                                                 
            zipf.write(browsePath, name)
            #
            name=bmet.getMetadataValue(browse_metadata.BROWSE_METADATA_REPORT_NAME)
            path = "%s/%s" % (folder, name)
            zipf.write(path, name)
        #

        # write product reports
        zipf.write(self.reportFullPath, os.path.split(self.reportFullPath)[1])
        # write sip report
        zipf.write(self.sipFullPath, os.path.split(self.sipFullPath)[1])
        
        zipf.close()

    #
    # control that the xml is well formatted, if not save it on disk
    #
    def formatXml(self, data=None, path=None, type=None):
        res=None
        try:
            helper=xmlHelper.XmlHelper()
            helper.parseData(data)
            # this will verify that xml is correct:
            res=helper.prettyPrint()
            #print "pretty print xml:\n%s" % res
            # keep original format, because is already indexed, to avoid mess with helper.prettyPrint()
            res=data
            #res=self.sanitizeXml(data)
        except Exception, e:
            # write it for debug
            path="%s/faulty_%s.xml" % (path, type)
            print "xml faulty %s data dump at path:%s" % (type, path)
            fd=open(path, 'w')
            fd.write(data)
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
    # 
    #
    def info(self):
        #raise Exception("STOP")
        print "\n\n##################################"
        print "#### START EOSIP Product Info ####"
        print "package name:%s" % self.packageName
        print "  Content:"
        print "   product name:%s" % self.productName
        print "   source product path:%s" % self.sourceProductPath
        print "   product shortName:%s" % self.productShortName
        print "   product tmpFolder:%s" % self.folder
        if len(self.sourceBrowsesPath)==0:
            print "   no sourceBrowsesPath"
        else:
            n=0
            for item in self.sourceBrowsesPath:
                print "   sourceBrowsesPath[%d]:%s" % (n, item)
                n=n+1
        if len(self.browsesReportInfo)==0:
            print "   no browse report"
        else:
            n=0
            for item in self.browsesReportInfo:
                print "   browse report info[%d]:%s" % (n, item)
                n=n+1
        print "   reportFullPath;%s" % self.reportFullPath
        print "   browseFullPath;%s" % self.browseFullPath
        print "   sipFullPath;%s" % self.sipFullPath
        print "#### END EOSIP Product Info   ####\n##################################\n"



if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=EOSIP_Product("d:\gilles\dev\M01_abcdefgfhj_20020920T100345.txt")
        p.getMetadataInfo()
        p.addBrowse('C:\Users\glavaux\Shared\LITE\Spot\SP1\scene01\imagery.tif', None)
        p.addBrowse('C:\Users\glavaux\Shared\LITE\Spot\SP1\scene01\imagery2.tif', None)
    except Exception, err:
        log.exception('Error from throws():')

