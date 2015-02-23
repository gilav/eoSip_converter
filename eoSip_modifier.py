#
# An EoSip modifier. It follows the Ingester workflow, + perform sevaral things (noted + hereafter). So it does is:
#  - Ingester works as usual, do the doOneProduct sequance
#  - here: create source product, an EoSip product
#  - here: + load the source products
#  - here: + extract source metadata
#  - here: create destination product
#  - Ingester build dest products names, create eoProduct tmp folder, extract metadata (overhead!), create reports
#  - here: do modifyEoSip:
#       - copy real .SI .MD .QR reports file in eoProduct tmp folder
#  - here: write destProduct
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
from esaProducts import eosip_product, eosip_product_helper
from esaProducts import metadata, browse_metadata
from esaProducts import definitions_EoSip,formatUtils
from definitions_EoSip import rep_footprint, sipBuilder
from namingConvention import NamingConvention
import imageUtil




class EoSip_modifier(ingester.Ingester):


        #
        # called before doing the various reports
        #
        def beforeReportsDone(self, processInfo):
                pass


        #
        # called after having done the various reports
        # 
        #
        def afterReportsDone(self, processInfo):
                self.modifyEoSip(processInfo)
                

        #
        # called at the end of the doOneProduct, before the index/shopcart creation
        #
        def afterProductDone(self, processInfo):
                pass
        
    
        #
        # Override
        #
        # create the source product, load it, extract metadata
        # all this has to be done, to be able to create a destinationProduct/workfolder with correct name pattern
        #  which are build using name patterm, which need correct metadata
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            processInfo.ingester=self
            eoSipProduct=eosip_product.EOSIP_Product(processInfo.srcPath)

            # set naming convention instance
            #print "######################## will use OUTPUT_SIP_PATTERN=%s" % self.OUTPUT_SIP_PATTERN
            namingConventionSip = NamingConvention(self.OUTPUT_SIP_PATTERN)
            eoSipProduct.setNamingConventionSipInstance(namingConventionSip)
            eoSipProduct.setNamingConventionEoInstance(namingConventionSip)

            
            processInfo.srcProduct = eoSipProduct
            eoSipProduct.processInfo = processInfo
            met=metadata.Metadata(processInfo.ingester.mission_metadatas)
            met.setOtherInfo("TYPOLOGY_SUFFIX", processInfo.ingester.TYPOLOGY)
            met.label='Source product'
            self.logger.info(" EoSip source created")
            processInfo.addLog(" - EoSip source created")

            # load source product
            eoSipProduct.loadProduct()
            numAdded=eoSipProduct.extractMetadata(met)
            self.logger.info(" number of metadata added:%s" % numAdded)
            processInfo.addLog(" number of metadata added:%s" % numAdded)

            print "\n###\n###\n###\nSOURCE METADATA:%s\n###\n###\n###\n" % met.toString()


        #
        # Override
        #
        # create destination product
        #
        def createDestinationProduct(self, processInfo):
            global debug,logger
            eosipP=eosip_product.EOSIP_Product()
            eosipP.sourceProductPath = processInfo.srcPath

            # set naming convention instance
            namingConventionSip = NamingConvention(self.OUTPUT_SIP_PATTERN)
            eosipP.setNamingConventionSipInstance(namingConventionSip)
            eosipP.setNamingConventionEoInstance(namingConventionSip)
            
            # set source product metadata
            print "\n###\n###\n###\nFROM SRC PRODUCT METADATA:%s\n###\n###\n###\n" % processInfo.srcProduct.metadata.toString()
            eosipP.setMetadata(processInfo.srcProduct.metadata)
            #
            eosipP.metadata.setOtherInfo("TYPOLOGY_SUFFIX", processInfo.ingester.TYPOLOGY)
            #
            eosipP.metadata.label='dest product'
            print "\n###\n###\n###\nFROM DEST PRODUCT METADATA:%s\n###\n###\n###\n" % eosipP.metadata.toString()

            processInfo.destProduct = eosipP
            
            self.logger.info(" EoSip dest product created")
            processInfo.addLog(" - EoSip dest product created")


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
                pass


        #
        # Override
        #
        # unneeded because is done when source product is created/loaded
        #
        def extractMetadata(self,met,processInfo):
            pass
            #processInfo.addLog("- will extract metadata from src product")
            #self.logger.info(" will extract metadata from src product")
            # fill metadata object
            #numAdded=processInfo.srcProduct.extractMetadata(met)                                            
            #self.logger.debug("number of metadata added:%d" % numAdded)



        #
        # Override
        #
        def makeBrowses(self, processInfo):
                pass                    


        #
        # after that the  various reports are created (based on the source product),  modify them to be ready to rewrite product
        #
        def modifyEoSip(self, processInfo):
                # flag product as workingOn, create the workingOn fodler
                processInfo.srcProduct.startWorkingOn()

                processInfo.addLog("\n\n\n##############################################\n##############################################\nModify src EoSip:%s" % processInfo.srcProduct.info())
                self.logger.info("\n\n\n##############################################\n##############################################\nModify src EoSip:%s" % processInfo.srcProduct.info())

                processInfo.addLog("\n dest EoSip:%s" % processInfo.destProduct.info())
                self.logger.info("\n dest EoSip:%s" % processInfo.destProduct.info())

                
                # get source oSip pieces, copy them in dest product workfolder, alter what we want to change
                self.eoSipHelper = eosip_product_helper.Eosip_product_helper(processInfo.srcProduct)
                # md part
                name, content = self.eoSipHelper.getMdPart()
                processInfo.addLog(" MD CONTENT:%s" % content)
                self.logger.info(" MD CONTENT:%s" % content)
                # write it
                self.reportFullPath="%s/%s" % (processInfo.destProduct.folder, name)
                fd=open(self.reportFullPath, "w")
                fd.write(content)
                fd.close()
                if self.debug!=0:
                    print "   product MD report written at path:%s" % self.reportFullPath
                

                # si part
                name, content = self.eoSipHelper.getSiPart()
                processInfo.addLog(" SI CONTENT:%s" % content)
                self.logger.info(" SI CONTENT:%s" % content)
                # write it
                self.reportFullPath="%s/%s" % (processInfo.destProduct.folder, name)
                fd=open(self.reportFullPath, "w")
                fd.write(content)
                fd.close()
                if self.debug!=0:
                    print "   product SI report written at path:%s" % self.reportFullPath

                # optional browse part
                try:
                        name, content = self.eoSipHelper.getBrowsePart(0)
                        processInfo.addLog(" browse 0 CONTENT:%s" % content)
                        self.logger.info(" browse 0 CONTENT:%s" % content)
                        # write it
                        self.reportFullPath="%s/%s" % (processInfo.destProduct.folder, name)
                        fd=open(self.reportFullPath, "w")
                        fd.write(content)
                        fd.close()
                        if self.debug!=0:
                            print "   product BR report written at path:%s" % self.reportFullPath
                except:
                        processInfo.addLog(" no browse 0 CONTENT")
                        self.logger.info(" no browse 0 CONTENT") 

                # optional qr part
                try:
                        name, content = self.eoSipHelper.getQrPart()
                        processInfo.addLog(" QR CONTENT:%s" % content)
                        self.logger.info(" QR CONTENT:%s" % content)
                        # write it
                        self.reportFullPath="%s/%s" % (processInfo.destProduct.folder, name)
                        fd=open(self.reportFullPath, "w")
                        fd.write(content)
                        fd.close()
                        if self.debug!=0:
                            print "   product QR report written at path:%s" % self.reportFullPath
                except:
                        processInfo.addLog(" no QR CONTENT")
                        self.logger.info(" no QR CONTENT")


        #
        #
        #
        def changeMdPart(self, dataIn, workingMdFilePath=None):
                pass
                

        #
        # Override
        #
        # output the Eo-Sip profuct in the destination folder
        # keep source product relative path
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
                        processInfo.addLog("  ok, writen well\n%s" % processInfo.destProduct.info())
                        self.logger.info(" ok, writen well\n%s" % processInfo.destProduct.info())

                        # make a thumbnail FOR TEST
                        if processInfo.create_thumbnail==1:
                                self.make_thumbnail(processInfo, firstPath)
                                # move also browse image
                                self.move_browse(processInfo, firstPath)

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

                




if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            modifier = EoSip_modifier()
            modifier.starts(sys.argv)
            
        else:
            print "syntax: python eoSip_modifier_xxx.py -c configuration_file.cfg [-l list_of_product_file]"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
