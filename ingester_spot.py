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
import shutil
from base import ingester
from esaProducts import dimap_spot_product, eosip_product
from esaProducts import metadata, browse_metadata
from esaProducts import definitions_EoSip,formatUtils
#from definitions_EoSip import rep_rectifiedBrowse
from definitions_EoSip import rep_footprint, sipBuilder
import imageUtil




class ingester_spot(ingester.Ingester):

    
        #
        # Override
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            dimapP = dimap_spot_product.Dimap_Spot_Product(processInfo.srcPath)
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
            met.setMetadataPair(metadata.METADATA_PRODUCT_SIZE, size)
            met.setMetadataPair(metadata.METADATA_GENERATION_TIME, time.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.logger.debug("number of metadata added:%d" % numAdded)

            # build typecode, set stop datetime = start datetime
            met.setMetadataPair(metadata.METADATA_STOP_DATE, met.getMetadataValue(metadata.METADATA_START_DATE))
            met.setMetadataPair(metadata.METADATA_STOP_TIME, met.getMetadataValue(metadata.METADATA_START_TIME))

            # extrack track frome from DATASET_ID. is like: SCENE 4 020-263 07/05/26 11:33:41 1 I
            try:
                    trackFrame=met.getMetadataValue(metadata.METADATA_DATASET_NAME).split(' ')[2]
                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ trackFrame:%s" % trackFrame
                    if 1==1 and trackFrame!=None and trackFrame.find('-')>0:
                            track=trackFrame.split('-')[0]
                            # supress possible /
                            if track.find('/')>0:
                                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ track has /:'%s'"  % track
                                    track=track[0:track.find('/')-1]
                            track=formatUtils.normaliseNumber(track, 3, '0')
                            frame=trackFrame.split('-')[1]
                            # supress possible /
                            if frame.find('/')>0:
                                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ frame has /:'%s'"  % frame
                                    frame=frame[0:track.find('/')-1]
                            frame=formatUtils.normaliseNumber(frame, 3, '0')
                            met.setMetadataPair(metadata.METADATA_TRACK, track)
                            met.setMetadataPair(metadata.METADATA_FRAME, frame)
                            met.setMetadataPair('METADATA_WRS_LONGITUDE_GRID_NORMALISED', track)
                            met.setMetadataPair('METADATA_WRS_LATITUDE_GRID_NORMALISED', frame)
                                    
                    #else:
                            #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ no - in trackFrame:%s" % trackFrame
                            
            except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print "Error %s  %s\n%s" %  (exc_type, exc_obj, traceback.format_exc())
                
            
            
            
            # get additionnal metadata from optionnal dataProvider:we want the track and frame
            # dataProvider key are METADATA_TRACK or METADATA_FRAME
            productId=None
            if len(self.dataProviders)>0:
                    #print "@@@@@@@@@@@@@@@@@@@@ extract using dataProviders:%s" % self.dataProviders
                    #print "@@@@@@@@@@@@@@@@@@@@         key:%s" % met.getMetadataValue(metadata.METADATA_ORIGINAL_NAME)
                    # look the one for the mission
                    for item in self.dataProviders.keys():
                            #print "@@@@@@@@@@@@@@@@@@@@ doing dataProviders item:%s" % item
                            if item == metadata.METADATA_TRACK:  # fiel is mandatory
                                    # what value do we have?
                                    tmp = met.getMetadataValue(metadata.METADATA_TRACK)
                                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current TRACK:%s" % tmp
                                    if tmp==None or tmp==sipBuilder.VALUE_NOT_PRESENT:
                                            #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current TRACK is:%s" % tmp
                                            adataProvider=self.dataProviders[item]
                                            #print "@@@@@@@@@@@@@@@@@@@@ dataProviders match TRACK:%s" % adataProvider
                                            # need to query using the product original filename like:N00-W075_AVN_20090804_PRO_0
                                            track=adataProvider.getRowValue(met.getMetadataValue(metadata.METADATA_ORIGINAL_NAME))
                                            #print "@@@@@@@@@@@@@@@@@@@@ track:%s" % track
                                            if track != None and len(track.strip())==0:
                                                    track='0000'
                                            met.setMetadataPair(metadata.METADATA_TRACK, track)

                            elif item == metadata.METADATA_FRAME:  # fiel is mandatory
                                    # what value do we have?
                                    tmp = met.getMetadataValue(metadata.METADATA_FRAME)
                                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current FRAME:%s" % tmp
                                    if tmp==None or tmp==sipBuilder.VALUE_NOT_PRESENT:
                                            print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current FRAME is:%s" % tmp
                                            adataProvider=self.dataProviders[item]
                                            #print "@@@@@@@@@@@@@@@@@@@@ dataProviders match FRAME:%s" % adataProvider
                                            # need to query using the product original filename like:N00-W075_AVN_20090804_PRO_0
                                            frame=adataProvider.getRowValue(met.getMetadataValue(metadata.METADATA_ORIGINAL_NAME))
                                            #print "@@@@@@@@@@@@@@@@@@@@ frame:%s" % frame
                                            if frame != None and len(frame.strip())==0:
                                                    frame='0000'
                                            met.setMetadataPair(metadata.METADATA_FRAME, frame)

                            elif item == metadata.METADATA_PRODUCT_ID: # this is just a test
                                    # what value do we have?
                                    tmp = met.getMetadataValue(metadata.METADATA_PRODUCT_ID)
                                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current PRODUCT_ID:%s" % tmp
                                    if tmp==None or tmp==sipBuilder.VALUE_NOT_PRESENT:
                                            try:
                                                    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ current PRODUCT_ID is:%s" % tmp
                                                    adataProvider=self.dataProviders[item]
                                                    #print "@@@@@@@@@@@@@@@@@@@@ dataProviders match PRODUCT_ID:%s" % adataProvider
                                                    # need to query using the product original filename like:N00-W075_AVN_20090804_PRO_0
                                                    # productId is like: SP4-070526113337-9.HRI1_X__1P
                                                    productId=adataProvider.getRowValue(met.getMetadataValue(metadata.METADATA_ORIGINAL_NAME))
                                                    #print "@@@@@@@@@@@@@@@@@@@@ productId:%s" % productId
                                                    if productId==None:
                                                            raise Exception("%s has no PRODUCT_ID in csv file" % met.getMetadataValue(metadata.METADATA_ORIGINAL_NAME))
                                                    if productId != None and len(productId.strip())==0:
                                                            productId='N/A'
                                                    met.setMetadataPair(metadata.METADATA_PRODUCT_ID, productId)
                                            except:
                                                    pass
                                                    
            # refine
            processInfo.srcProduct.refineMetadata()

            # do a check: look if it's equal to metadata.METADATA_TYPECODE
            if productId!=None:
                    pos = productId.find('.')
                    if pos>0:
                            tmp1=productId[pos+1:]
                            tmp=met.getMetadataValue(metadata.METADATA_TYPECODE)
                            self.saveInfo("typeCodes.txt", tmp1)
                            if tmp!=tmp1:
                                    raise Exception("Mismatch: metadata.METADATA_TYPECODE vs metadata.METADATA_PRODUCT_ID[.*]:'%s'<==>'%s'" % (tmp, tmp1))



        #
        # Override
        # copy the source browse image into work folder
        # construct the browse_metadatareport footprint block(BROWSE_CHOICE): it is the rep:footprint for spot
        #
        def makeBrowses(self,processInfo):
            try:
                    browseSrcPath=processInfo.srcProduct.preview_path
                    browseExtension=definitions_EoSip.getBrowseExtension(0, definitions_EoSip.getDefinition('BROWSE_JPEG_EXT'))
                    browseDestPath="%s/%s.%s" % (processInfo.eosipTmpFolder, processInfo.destProduct.packageName, browseExtension)
                    shutil.copyfile(browseSrcPath, browseDestPath)
                    processInfo.destProduct.addSourceBrowse(browseDestPath, [])
                    processInfo.addLog("  browse image created:%s" %  (browseDestPath))
                    self.logger.info("  browse image created:%s" % browseDestPath)


                    # create browse choice for browse metadata report
                    bmet=processInfo.destProduct.browse_metadata_dict[browseDestPath]
                    #print "######\n######\n%s" % dir(definitions_EoSip)

                    
                    footprintBuilder=rep_footprint.rep_footprint()
                    #
                    print "###\n###\n### BUILD BROWSE CHOICE FROM METADATA:%s" % (processInfo.destProduct.metadata.toString())
                    browseChoiceBlock=footprintBuilder.buildMessage(processInfo.destProduct.metadata, "rep:browseReport/rep:browse/rep:footprint").strip()
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
                    #raise e

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

                        # copy the browse FOR TEST
                        try:
                                if len(processInfo.destProduct.sourceBrowsesPath)>0:
                                        tmp=os.path.split(processInfo.destProduct.sourceBrowsesPath[0])[1]
                                        tmpb=tmp.split('.')[-1]
                                        tmpa=tmp.split('.')[0:-1]
                                        thumbnail = "%s.TN.%s" % ("".join(tmpa),tmpb)
                                        processInfo.destProduct.metadata.setMetadataPair(metadata.METADATA_THUMBNAIL,thumbnail)
                                        thumbnail="%s/%s" % (firstPath, thumbnail)
                                        #shutil.copyfile("%s" % (processInfo.destProduct.sourceBrowsesPath[0]), "%s/%s" % (firstPath,tmp))
                                        imageUtil.makeJpeg("%s" % (processInfo.destProduct.sourceBrowsesPath[0]), thumbnail, 25 )
                                        print "####################################### %s/%s_TN.%s" % (firstPath,tmpa,tmpb)
                                
                                else:
                                        print "There is no brose to move to final folder"
                        except:
                                print " thubnail Error"
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                traceback.print_exc(file=sys.stdout)

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
            ingester = ingester_spot()
            ingester.starts(sys.argv)
            
        else:
            print "syntax: python ingester_xxx.py configuration_file.cfg"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
