#
# This is a specialized class that ingest Ikonos dataset
#
# For Esa/ lite dissemination project
#
# Serco 04/2014
# Lavaux Gilles
#
# 23/04/2014: V: 0.1
#
#
#
import os, sys
import time
import zipfile
import traceback
import shutil
from base import ingester
from esaProducts import netCDF_reaper_product, eosip_product
from esaProducts import metadata
from esaProducts import definitions_EoSip
import imageUtil




class ingester_reaper(ingester.Ingester):

        #
        # called at the end of the doOneProduct, before the index/shopcart creation
        #
        def afterProductDone(self, processInfo):
                pass
        
        #
        # Override
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            processInfo.ingester=self
            processInfo.srcProduct = netCDF_reaper_product.netCDF_reaper_Product(processInfo.srcPath)

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
                pass

            
        #
        # Override
        #
        def prepareProducts(self,processInfo):
                processInfo.addLog(" prepare product in:%s" % (processInfo.workFolder))
                self.logger.info(" prepare product");
                print " #### copy src file '%s' into '%s'" % (processInfo.srcProduct.path, "%s/%s" % (processInfo.workFolder, processInfo.srcProduct.origName))
                shutil.copyfile(processInfo.srcProduct.path, "%s/%s" % (processInfo.workFolder, processInfo.srcProduct.origName))
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

            # refine
            processInfo.srcProduct.refineMetadata()


        #
        # Override
        #
        def makeBrowses(self,processInfo):
            pass

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
            ingester = ingester_reaper()
            ingester.starts(sys.argv)
            
        else:
            print "syntax: python ingester_xxx.py configuration_file.cfg"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
