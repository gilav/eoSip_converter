#
# This is a specialized class that ingest AEolus dataset
#
# For Esa/ lite dissemination project
#
# Serco 01/2015
# Lavaux Gilles
#
# 07/04/2014: V: 0.1
#
#
#
import os, sys
import time
import zipfile
import traceback
import shutil
from base import ingester
from esaProducts import aeolus_product, eosip_product
from esaProducts import metadata, browse_metadata
from esaProducts import definitions_EoSip, namingConvention ,formatUtils
from definitions_EoSip import rep_footprint, sipBuilder, rep_rectifiedBrowse
from namingConvention import NamingConvention
from namingConvention_aeolus import NamingConvention_Aeolus
import imageUtil


# minumunm config version that can be use
MIN_CONFIG_VERSION=1.0

class ingester_aeolus(ingester.Ingester):

        #
        # config version is like: name_floatVersion
        #
        def checkConfigurationVersion(self):
                global MIN_CONFIG_VERSION
                self._checkConfigurationVersion(self.CONFIG_VERSION, MIN_CONFIG_VERSION)

        #
        # called before doing the various reports
        # change the mapping of href to METADATA_PACKAGENAME
        #
        def beforeReportsDone(self, processInfo):
                processInfo.destProduct.metadata.alterMetadataMaping('href', metadata.METADATA_FULL_PACKAGENAME)

        #
        # called after having done the various reports
        #
        def afterReportsDone(self, processInfo):
                # modify the MD.XML file
                # add ldr namespace
                #"xmlns:eop="http://www.opengis.net/eop/2.1" xmlns:ldr="http://www.opengis.net/ldr/2.1""
                fd = open(processInfo.destProduct.reportFullPath, 'r')
                mdXmlData=fd.read()
                fd.close()
                print "Will modify MD.XML data:\n%s" % mdXmlData

                # add ldr namespace
                mdXmlDataModified = mdXmlData.replace('xmlns:eop="http://www.opengis.net/eop/2.1"', 'xmlns:eop="http://www.opengis.net/eop/2.1" xmlns:ldr="http://www.opengis.net/ldr/2.1"')

                #modify root node namespace
                mdXmlDataModified = mdXmlDataModified.replace('<eop:EarthObservation xmlns:', '<ldr:EarthObservation xmlns:')
                mdXmlDataModified = mdXmlDataModified.replace('</eop:EarthObservation>', '</ldr:EarthObservation>')

                # add footprint
                FOOTPRINT='  <om:featureOfInterest>\n\
		<ldr:Footprint gml:id="@@PACKAGENAME@@_5">\n\
			<eop:multiExtentOf/>\n\
			<ldr:nominalTrack>\n\
				<gml:MultiCurve gml:id="@@PACKAGENAME@@_6">\n\
					<gml:curveMember>\n\
						<gml:LineString gml:id="@@PACKAGENAME@@_7">\n\
							<gml:posList>-60.11159 -49.394531 -22.355494 -19.863281 51.777811 18.457031 78.611509 63.808594</gml:posList>\n\
						</gml:LineString>\n\
					</gml:curveMember>\n\
				</gml:MultiCurve>\n\
			</ldr:nominalTrack>\n\
		</ldr:Footprint>\n\
  </om:featureOfInterest>'
                productName = processInfo.destProduct.metadata.getMetadataValue(metadata.METADATA_IDENTIFIER)
                tmp = FOOTPRINT.replace('@@PACKAGENAME@@', productName)
                print "FOOTPRINT:\n%s" % tmp
                mdXmlDataModified = mdXmlDataModified.replace('  <om:featureOfInterest/>', tmp)

                # fix index of:METADATA_PACKAGENAME_5  to METADATA_PACKAGENAME_7
                mdXmlDataModified = mdXmlDataModified.replace('eop:EarthObservationResult gml:id="%s_5"' % (productName) , 'eop:EarthObservationResult gml:id="%s_8"' % (productName))
                
                print "modified MD.XML data:\n%s" % mdXmlDataModified
                fd = open(processInfo.destProduct.reportFullPath, 'w')
                fd.write(mdXmlDataModified)
                fd.close()
                

        #
        # called at the end of the doOneProduct, before the index/shopcart creation
        # set the METADATA_BOUNDING_BOX_CW_CLOSED into FOOTPRINT to hace 'correct' browse display in EoliSa
        #
        def afterProductDone(self, processInfo):
                #print " ####################################\n ####################################\nset footprint for shopcart/index to:%s" % processInfo.destProduct.metadata.getMetadataValue(metadata.METADATA_BOUNDING_BOX_CW_CLOSED)
                #processInfo.destProduct.metadata.setMetadataPair(metadata.METADATA_FOOTPRINT_CW, processInfo.destProduct.metadata.getMetadataValue(metadata.METADATA_BOUNDING_BOX_CW_CLOSED))
                pass
        
    
        #
        # Override
        #
        # create the source product (from the .DBL file), but only if the associated (.HDF) is present
        # 
        #
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            # find/test the associated file (.HDF)
            processInfo.srcPath=processInfo.srcPath.replace('\\','/')
            hdfPath = processInfo.srcPath.replace('.DBL','.HDR')
            if os.path.exists(hdfPath):
                    aeolusP = aeolus_product.Aeolus_Product(processInfo.srcPath, hdfPath)
                    # need the filename pattern
                    aeolusP.OUTPUT_EO_PATTERN = self.OUTPUT_EO_PATTERN
                    processInfo.srcProduct = aeolusP
            else:
                    raise Exception("can not find associated .HDF file:%s" % hdfPath)

        #
        # Override
        #
        def createDestinationProduct(self, processInfo):
            global debug,logger
            eosipP=eosip_product.EOSIP_Product()
            eosipP.sourceProductPath = processInfo.srcPath
            processInfo.destProduct = eosipP
            
            # set naming convention instance
            namingConventionSip = NamingConvention(self.OUTPUT_SIP_PATTERN)
            processInfo.destProduct.setNamingConventionSipInstance(namingConventionSip)

            # level 0 and 1 have filename convention EOLUS_PATTERN_INSTANCE_GENERIC_DTOV
            # level 2 have convention EOLUS_PATTERN_INSTANCE_GENERIC_DDV
            
            namingConventionEo = NamingConvention_Aeolus(self.OUTPUT_EO_PATTERN)
            processInfo.destProduct.setNamingConventionEoInstance(namingConventionEo)

            # we want to keep the product original name:
            processInfo.destProduct.eoProductName=processInfo.srcProduct.origName

            #
            self.logger.info(" Eo-Sip class created")
            processInfo.addLog("\n - Eo-Sip class created")
                    
        #
        # Override
        #
        def verifySourceProduct(self, processInfo):
                processInfo.addLog(" - verifying product: %s" % (processInfo.srcPath))
                self.logger.info(" verifying product")
                fh = open(processInfo.srcPath, 'rb')
                zf = zipfile.ZipFile(fh)
                ok = zf.testzip()
                fh.close()
                if ok is not None:
                        self.logger.error("  Zip file is corrupt:%s" % processInfo.srcPath)
                        self.logger.error("  First bad file in zip: %s" % ok)
                        processInfo.addLog("  => Zip file is corrupt:%s" % processInfo.srcPath)
                        raise Exception("Zip file is corrupt:%s" % processInfo.srcPath)
                else:
                    self.logger.info("  Zip file is ok")
                    processInfo.addLog("  => Zip file is ok")

            
        #
        # Override
        #
        def prepareProducts(self,processInfo):
                processInfo.addLog("\n - prepare product, will extract inside working folder:%s" % (processInfo.workFolder))
                self.logger.info(" prepare product")
                processInfo.srcProduct.extractToPath(processInfo.workFolder, processInfo.test_dont_extract)
                processInfo.addLog("  => extracted inside:%s" % (processInfo.workFolder))
                self.logger.info("  extracted inside:%s" % (processInfo.workFolder))

        #
        # Override
        #
        def extractMetadata(self,met,processInfo):
            processInfo.addLog("\n - will extract metadata from src product")
            self.logger.info(" will extract metadata from src product")
            # fill metadata object
            numAdded=processInfo.srcProduct.extractMetadata(met)
            size=processInfo.srcProduct.getSize()
            met.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, size)
            met.setMetadataPair(metadata.METADATA_GENERATION_TIME, time.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.logger.debug("number of metadata added:%d" % numAdded)
            
                                                
            # refine
            processInfo.srcProduct.refineMetadata()


        #
        #
        #
        def makeBrowseChoiceBlock(self, processInfo, metadata):

            # create browse choice for browse metadata report
            reportBuilder=rep_rectifiedBrowse.rep_rectifiedBrowse()
            if self.debug!=0:
                    print "###\n###\n### BUILD BROWSE CHOICE FROM METADATA:%s" % (processInfo.destProduct.metadata.toString())
            browseChoiceBlock=reportBuilder.buildMessage(processInfo.destProduct.metadata, "rep:rectifiedBrowse").strip()
            if self.debug!=0:
                    print "browseChoiceBlock:%s" % (browseChoiceBlock)
            metadata.setMetadataPair(browse_metadata.BROWSE_METADATA_BROWSE_CHOICE, browseChoiceBlock)

            

        #
        # Override
        #
        # get the logo png image (defined as ressource)
        #
        def makeBrowses(self, processInfo):
                try:
                        browseSrcPath = self.ressourcesProvider.getRessourcePath('logo')
                        self.logger.error("logo path:%s" % browseSrcPath)
                        processInfo.addLog("logo path:%s" % browseSrcPath)

                        # copy logo in workfolder, name it well
                        browseExtension=definitions_EoSip.getBrowseExtension(0, definitions_EoSip.getDefinition('BROWSE_PNG_EXT'))
                        browseDestPath="%s/%s.%s" % (processInfo.eosipTmpFolder, processInfo.destProduct.eoProductName, browseExtension)
                        shutil.copyfile(browseSrcPath, browseDestPath)

                        # add browse to dest product, this create the browse metadata   
                        processInfo.destProduct.addSourceBrowse(browseDestPath, [])

                        # create browse choice for browse metadata report
                        bmet=processInfo.destProduct.browse_metadata_dict[browseDestPath]

                        self.makeBrowseChoiceBlock(processInfo, bmet)

                        # set the browse type (if not default one(i.e. product type code))for the product metadata report BROWSES block
                        # if specified in configuration
                        tmp = processInfo.srcProduct.metadata.getMetadataValue(metadata.METADATA_BROWSES_TYPE)
                        if tmp != None:
                            bmet.setMetadataPair(metadata.METADATA_BROWSES_TYPE, tmp)

                        # idem for METADATA_CODESPACE_REFERENCE_SYSTEM
                        tmp = processInfo.srcProduct.metadata.getMetadataValue(metadata.METADATA_CODESPACE_REFERENCE_SYSTEM)
                        if tmp != None:
                            bmet.setMetadataPair(metadata.METADATA_CODESPACE_REFERENCE_SYSTEM, tmp)

                        processInfo.addLog("  browse image created:%s" %  (browseDestPath))
                        self.logger.info("  browse image created:%s" % browseDestPath)
                        
                except Exception, e:
                    try:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            errorMsg="Error generating browse: error type:%s  exec_obj:%s" %  (exc_type, exc_obj)
                            self.logger.error(errorMsg)
                            processInfo.addLog("%s" %  (errorMsg))
                            processInfo.addLog("%s" %  (traceback.format_exc()))
                            print "ERROR: make browse error: %s\n%s" % (errorMsg, traceback.format_exc())
                    except Exception, ee:
                            self.logger.error("  problem adding browse generation error in processInfo")
                            pass
                    #raise e
                



        #
        # Override
        #
        # output the Eo-Sip profuct in the destination folder
        # take the first rule and put the product in the resulting folder
        # create link for the other rules if any
        #
        def output_eoSip(self, processInfo, basePath, pathRules, overwrite=None):
                processInfo.addLog("\n - will output eoSip; basePath=%s" %  (basePath))
                self.logger.info(" will output eoSip; basePath=%s" %  (basePath))
                # copy eoSip in first path
                # make links in other paths
                outputProductResolvedPaths = processInfo.destProduct.getOutputFolders(basePath, pathRules)
                if len(outputProductResolvedPaths)==0:
                        processInfo.addLog("   ERROR: no product resolved path")
                        self.logger.info(" ERROR: no product resolved path")
                        raise Exception("no product resolved path")
                else:
                        # output in first path
                        firstPath=outputProductResolvedPaths[0]
                        processInfo.addLog("  Eo-Sip product will be writen in folder:%s" %  (firstPath))
                        self.logger.info("  Eo-Sip product will be writen in folder:%s" %  (firstPath))
                        processInfo.destProduct.writeToFolder(firstPath, overwrite)
                        processInfo.addLog("  ok, writen well")
                        self.logger.info(" ok, writen well")

                        # output link in other path
                        i=0
                        for item in outputProductResolvedPaths:
                                if i>0:
                                        otherPath="%s" % (item)
                                        self.logger.info("  create also (linked?) eoSip product at tree path[%d] is:%s" %(i, item))
                                        processInfo.addLog("  create also (linked?) eoSip product at tree path[%d] is:%s" %(i, item))
                                        processInfo.destProduct.writeToFolder(basePath, overwrite)
                                        processInfo.addLog("  Eo-Sip product link writen in folder[%d]:%s\n" %  (i, otherPath))
                                        self.logger.info("  Eo-Sip product link writen in folder[%d]:%s\n" %  (i, otherPath))
                                i=i+1



if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            ingester = ingester_aeolus()
            ingester.debug=1
            ingester.starts(sys.argv)
            
        else:
            print "syntax: python ingester_xxx.py -c configuration_file.cfg [-l list_of_product_file]"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
