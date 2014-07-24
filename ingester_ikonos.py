#
# This is a specialized class that ingest Ikonos dataset
#
# For Esa/ lite dissemination project
#
# Serco 04/2014
# Lavaux Gilles & Simone Garofalo
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
from esaProducts import ikonos_product, eosip_product
from esaProducts import metadata, browse_metadata
from esaProducts import definitions_EoSip
from definitions_EoSip import rep_footprint
import imageUtil




class ingester_ikonos(ingester.Ingester):

    
        #
        # Override
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            processInfo.ingester=self
            processInfo.srcProduct = ikonos_product.Ikonos_Product(processInfo.srcPath)

        #
        # Override
        #
        def createDestinationProduct(self, processInfo):
            global debug,logger
            eosipP=eosip_product.EOSIP_Product()
            eosipP.sourceProductPath = processInfo.srcPath
            processInfo.destProduct = eosipP
            self.logger.info(" Eo-Sip product created")
            processInfo.addLog(" Eo-Sip product created")
                    
        #
        # Override
        #
        def verifySourceProduct(self, processInfo):
                return
                processInfo.addLog(" verifying product:%s" % (processInfo.srcPath))
                self.logger.info(" verifying product");
                fh = open(processInfo.srcPath, 'rb')
                zf = zipfile.ZipFile(fh)
                ok = zf.testzip()
                fh.close()
                if ok is not None:
                        self.logger.error("  Zip file is corrupt:%s" % processInfo.srcPath)
                        self.logger.error("  First bad file in zip: %s" % ok)
                        processInfo.addLog("  Zip file is corrupt:%s" % processInfo.srcPath)
                        raise Exception("Zip file is corrupt:%s" % processInfo.srcPath)
                else:
                    self.logger.info("  Zip file is ok")
                    processInfo.addLog("  Zip file is ok")

            
        #
        # Override
        #
        def prepareProducts(self,processInfo):
                processInfo.addLog(" prepare product in:%s" % (processInfo.workFolder))
                self.logger.info(" prepare product");
                processInfo.srcProduct.extractToPath(processInfo.workFolder)
                processInfo.addLog("  extracted inside:%s" % (processInfo.workFolder))
                self.logger.info("  extracted inside:%s" % (processInfo.workFolder))

        #
        # Override
        #
        def extractMetadata(self,met,processInfo):
            # fill metadata object
            numAdded=processInfo.srcProduct.extractMetadata(met)
            size=processInfo.srcProduct.getSize()
            met.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, size)
            met.setMetadataPair(metadata.METADATA_GENERATION_TIME, time.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.logger.debug("number of metadata added:%d" % numAdded)

            # build typecode, set stop datetime = start datetime
            met.setMetadataPair(metadata.METADATA_STOP_DATE, met.getMetadataValue(metadata.METADATA_START_DATE))
            met.setMetadataPair(metadata.METADATA_STOP_TIME, met.getMetadataValue(metadata.METADATA_START_TIME))
            # refine
            processInfo.srcProduct.refineMetadata()


        #
        # Override
        #
        def makeBrowses(self,processInfo):
            try:
                    #browseSrcPath="%s/%s" % (processInfo.workFolder , processInfo.srcProduct.PREVIEW_NAME)
                    browseSrcPath=processInfo.srcProduct.preview_path
                    browseExtension=definitions_EoSip.getBrowseExtension(0, definitions_EoSip.getDefinition('BROWSE_JPEG_EXT'))
                    browseDestPath="%s/%s.%s" % (processInfo.eosipTmpFolder, processInfo.destProduct.packageName, browseExtension)
                    shutil.copyfile(browseSrcPath, browseDestPath)
                    processInfo.destProduct.addSourceBrowse(browseDestPath, [])
                    processInfo.addLog("  browse image created:%s" %  (browseDestPath))
                    self.logger.info("  browse image created:%s" % browseDestPath)

                    # create browse choice for browse metadata report
                    bmet=processInfo.destProduct.browse_metadata_dict[browseDestPath]
                    print "######\n######\n%s" % dir(definitions_EoSip)

                    
                    reportBuilder=rep_footprint.rep_footprint()
                    #
                    print "###\n###\n### BUILD BROWSE CHOICE FROM METADATA:%s" % (processInfo.destProduct.metadata.toString())
                    browseChoiceBlock=reportBuilder.buildMessage(processInfo.destProduct.metadata, "rep:browseReport/rep:browse/rep:footprint").strip()
                    if self.debug!=-1:
                            print "browseChoiceBlock:%s" % (browseChoiceBlock)
                    bmet.setMetadataPair(browse_metadata.BROWSE_METADATA_BROWSE_CHOICE, browseChoiceBlock)

                    # set the browse type (if not default one(i.e. product type code))for the product metadata report BROWSES block
                    # if specified in configuration
                    tmp = processInfo.srcProduct.metadata.getMetadataValue(metadata.METADATA_BROWSES_TYPE)
                    if tmp != None:
                            bmet.setMetadataPair(metadata.METADATA_BROWSES_TYPE, tmp)

                    # idem for METADATA_CODESPACE_REFERENCE_SYSTEM
                    tmp = processInfo.srcProduct.metadata.getMetadataValue(metadata.METADATA_CODESPACE_REFERENCE_SYSTEM)
                    if tmp != None:
                            bmet.setMetadataPair(metadata.METADATA_CODESPACE_REFERENCE_SYSTEM, tmp)
                    
            except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    errorMsg="Error generating browse:%s  %s\n%s" %  (exc_type, exc_obj, traceback.format_exc())
                    self.logger.error(errorMsg)
                    processInfo.addLog="%s" %  (errorMsg)
                    processInfo.addLog="%s" %  (traceback.format_exc())
                    raise e

        #
        # Override
        #
        # output the Eo-Sip profuct in the destination folder
        # take the first rule and put the product in the resulting folder
        # create link for the other rules if any
        #
        def output_eoSip(self, processInfo, basePath, pathRules, overwrite=None):
                self.logger.info("  output_eoSip: basePath=%s" %  (basePath))
                # copy eoSip in first path
                # make links in other paths
                outputProductResolvedPaths = processInfo.destProduct.getOutputFolders(basePath, pathRules)
                if len(outputProductResolvedPaths)==0:
                        raise Exception("no product resolved path")
                else:
                        # output in first path
                        firstPath=outputProductResolvedPaths[0]
                        processInfo.addLog("  Eo-Sip product writen in folder:%s\n" %  (firstPath))
                        self.logger.info("  Eo-Sip product writen in folder:%s\n" %  (firstPath))
                        processInfo.destProduct.writeToFolder(firstPath, overwrite)

                        # output link in other path
                        i=0
                        for item in outputProductResolvedPaths:
                                if i>0:
                                        otherPath="%s" % (item)
                                        self.logger.info("  eoSip product tree path[%d] is:%s" %(i, item))
                                        processInfo.destProduct.writeToFolder(basePath, overwrite)
                                        processInfo.addLog("  Eo-Sip product link writen in folder[%d]:%s\n" %  (i, otherPath))
                                        self.logger.info("  Eo-Sip product link writen in folder[%d]:%s\n" %  (i, otherPath))
                                i=i+1



if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            ingester = ingester_ikonos()
            ingester.debug=0
            ingester.starts(sys.argv)
            
        else:
            print "syntax: python ingester_xxx.py configuration_file.cfg"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
