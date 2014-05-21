#
# This is a specialized class that ingest TropForest dataset
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
from base import ingester
from esaProducts import dimap_tropforest_product, eosip_product
from esaProducts import metadata, browse_metadata
from esaProducts import definitions_EoSip
from definitions_EoSip import rep_rectifiedBrowse
import imageUtil




class ingester_tropforest(ingester.Ingester):

    
        #
        # Override
        # this is the first function called by the base ingester
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            # set ingester in processInfo for later use
            processInfo.ingester=self
            dimapP = dimap_tropforest_product.Dimap_Tropforest_Product(processInfo.srcPath)
            processInfo.srcProduct = dimapP

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
            grid_lat=processInfo.srcProduct.extractGridFromFile("lat")
            grid_lon=processInfo.srcProduct.extractGridFromFile("lon")
            grid_lat_norm=processInfo.srcProduct.extractGridFromFileNormalised("lat")
            grid_lon_norm=processInfo.srcProduct.extractGridFromFileNormalised("lon")
            met.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, size)
            met.setMetadataPair('METADATA_WRS_LONGITUDE_GRID', grid_lon)
            met.setMetadataPair('METADATA_WRS_LATITUDE_GRID', grid_lat)
            met.setMetadataPair('METADATA_WRS_LONGITUDE_GRID_NORMALISED', grid_lon_norm)
            met.setMetadataPair('METADATA_WRS_LATITUDE_GRID_NORMALISED', grid_lat_norm)                    
            met.setMetadataPair(metadata.METADATA_FRAME, grid_lat_norm)
            met.setMetadataPair(metadata.METADATA_TRACK, grid_lon_norm)
            met.setMetadataPair(metadata.METADATA_GENERATION_TIME, time.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.logger.debug("number of metadata added:%d" % numAdded)

            # build typecode, set stop datetime = start datetime
            met.setMetadataPair(metadata.METADATA_STOP_DATE, met.getMetadataValue(metadata.METADATA_START_DATE))
            met.setMetadataPair(metadata.METADATA_STOP_TIME, met.getMetadataValue(metadata.METADATA_START_TIME))

            # get additionnal metadata from optionnal dataProvider:we want the orbit
            if len(self.dataProviders)>0:
                    print "@@@@@@@@@@@@@@@@@@@@ extract using dataProviders:%s" % self.dataProviders
                    # look the one for the mission
                    for item in self.dataProviders.keys():
                            if item.find(met.getMetadataValue(metadata.METADATA_PLATFORM))>=0:
                                    adataProvider=self.dataProviders[item]
                                    print "@@@@@@@@@@@@@@@@@@@@ dataProviders match mission:%s" % adataProvider
                                    # need to query using the product original filename like:N00-W075_AVN_20090804_PRO_0
                                    orbit=adataProvider.getRowValue(met.getMetadataValue(metadata.METADATA_DATASET_NAME))
                                    print "@@@@@@@@@@@@@@@@@@@@ orbit:%s" % orbit
                                    if len(orbit.strip())==0:
                                            orbit=None
                                    met.setMetadataPair(metadata.METADATA_ORBIT, orbit)
                                    break
                                    
                    

            # refine
            processInfo.srcProduct.refineMetadata()

                
        #
        #
        #
        def makeBrowseChoiceBlock(self, processInfo, metadata):
            # create browse choice for browse metadata report
            reportBuilder=rep_rectifiedBrowse.rep_rectifiedBrowse()
            print "###\n###\n### BUILD BROWSE CHOICE FROM METADATA:%s" % (processInfo.destProduct.metadata.toString())
            browseChoiceBlock=reportBuilder.buildMessage(processInfo.destProduct.metadata, "rep:rectifiedBrowse").strip()
            if self.debug==0:
                    print "browseChoiceBlock:%s" % (browseChoiceBlock)
            metadata.setMetadataPair(browse_metadata.METADATA_BROWSE_CHOICE, browseChoiceBlock)


        #
        # Override
        # make the jpeg brose image from the TIFF image
        # construct the browse_metadatareport footprint block: it is the rectifedBrowse for tropforest
        #
        def makeBrowses(self,processInfo):
            try:
                    browseSrcPath="%s/%s" % (processInfo.workFolder , processInfo.srcProduct.TIF_FILE_NAME)
                    browseExtension=definitions_EoSip.getBrowseExtension(0, definitions_EoSip.getDefinition('BROWSE_JPEG_EXT'))
                    browseDestPath="%s/%s.%s" % (processInfo.eosipTmpFolder, processInfo.destProduct.productShortName, browseExtension)
                    imageUtil.makeJpeg(browseSrcPath, browseDestPath, 50 )
                    processInfo.destProduct.addSourceBrowse(browseDestPath, [])

                    # create browse choice for browse metadata report
                    bmet=processInfo.destProduct.browse_metadata_dict[browseDestPath]
                    #reportBuilder=rep_rectifiedBrowse.rep_rectifiedBrowse()
                    #print "###\n###\n### BUILD BROWSE CHOICE FROM METADATA:%s" % (processInfo.destProduct.metadata.toString())
                    #browseChoiceBlock=reportBuilder.buildMessage(processInfo.destProduct.metadata, "rep:rectifiedBrowse").strip()
                    #if self.debug==0:
                    #        print "browseChoiceBlock:%s" % (browseChoiceBlock)
                    #bmet.setMetadataPair(browse_metadata.METADATA_BROWSE_CHOICE, browseChoiceBlock)
                    self.makeBrowseChoiceBlock(processInfo, bmet)
        
                    processInfo.addLog("  browse image created:%s" %  (browseDestPath))
                    self.logger.info("  browse image created:%s" % browseDestPath)
            except Exception, e:
                    try:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            errorMsg="Error generating browse: error type:%s  exec_obj:%s" %  (exc_type, exc_obj)
                            self.logger.error(errorMsg)
                            processInfo.addLog("%s" %  (errorMsg))
                            processInfo.addLog("%s" %  (traceback.format_exc()))
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
        def output_eoSip(self, processInfo, basePath, pathRules):
                self.logger.info("  output_eoSip: basePath=%s" %  (basePath))
                # copy eoSip in first path; make links in other paths: 
                
                # now done before in base_ingester.doOneProduct
                #self.outputProductResolvedPaths = processInfo.destProduct.getOutputFolders(basePath, pathRules)

                #
                if len(self.outputProductResolvedPaths)==0:
                        raise Exception("no product resolved path")
                else:
                        # output in first path
                        firstPath=self.outputProductResolvedPaths[0]
                        processInfo.addLog("  Eo-Sip product writen in folder:%s\n" %  (firstPath))
                        self.logger.info("  Eo-Sip product writen in folder:%s\n" %  (firstPath))
                        processInfo.destProduct.writeToFolder(firstPath)

                        # output link in other path
                        i=0
                        for item in self.outputProductResolvedPaths:
                                if i>0:
                                        otherPath="%s" % (item)
                                        self.logger.info("  eoSip product tree path[%d] is:%s" %(i, item))
                                        processInfo.destProduct.writeToFolder(basePath)
                                        processInfo.addLog("  Eo-Sip product link writen in folder[%d]:%s\n" %  (i, otherPath))
                                        self.logger.info("  Eo-Sip product link writen in folder[%d]:%s\n" %  (i, otherPath))
                                i=i+1



if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            ingester = ingester_tropforest()
            #ingester.debug=1
            ingester.readConfig(sys.argv[1])
            ingester.makeFolders()
            ingester.getMissionDefaults()
            if len(sys.argv)>2:
                ingester.setProductsList(sys.argv[2])
            else:
                    ingester.findProducts()
            ingester.processProducts()
            
        else:
            print "syntax: python ingester_xxx.py configuration_file.cfg"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
