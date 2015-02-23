#
# This is a specialized class that ingest Reaper ERS-RA dataset by cycle
# It differ from the reaper ingester in the following:
# - at startup just read the configuration, will use a listOfProduct file
# - will treat block of n products(cycle) from this list as one source product, it will end up in one EoSip package
#
# For Esa/ lite dissemination project
#
# Serco 11/2014
# Lavaux Gilles
#
# 23/04/2014: V: 0.1
#
#
#
import os,sys,inspect
import time
import zipfile
import traceback
import shutil
import urllib

from base import ingester
from esaProducts import directory_product, netCDF_reaper_product, eosip_product 
from esaProducts import metadata
from esaProducts import definitions_EoSip
from esaProducts import reaper_cycle
from namingConvention import NamingConvention
import imageUtil
from fileHelper import fileHelper

import indexCreator, shopcartCreator

from base import processInfo, infoKeeper
from satellites import ers1cycles,ers2cycles


# minumunm config version that can be use
MIN_CONFIG_VERSION=1.0

# the file holding the cycle ordered file
REAPER_PACKAGES='reaper_packages.txt'
REAPER_PACKAGES_FILES='reaper_packages_files.txt'

class ingester_reaper_cycle(ingester.Ingester):

        #
        # config version is like: name_floatVersion
        #
        def checkConfigurationVersion(self):
                global MIN_CONFIG_VERSION
                self._checkConfigurationVersion(self.CONFIG_VERSION, MIN_CONFIG_VERSION)
                
        #
        # called before doing the various reports
        #
        def beforeReportsDone(self, processInfo):
                pass

        
        #
        # called after having done the various reports
        #
        def afterReportsDone(self, processInfo):
                pass

        
        #
        # called at the end of the doOneProduct, before the index/shopcart creation
        #
        def afterProductDone(self, processInfo):
                pass
        
        
        #
        # Override
        #
        # create a directory product, add inside all cycle products
        #
        def createSourceProduct(self, processInfo):
            global debug,logger
            processInfo.srcProduct = reaper_cycle.Reaper_Cycle(processInfo.srcPath) #directory_product.Directory_Product(processInfo.srcPath)

            # add reaper files in src product
            self.logger.info(" add files from cycle %s in src product:" % processInfo.srcPath)
            for item in self.keeperFiles.getKeyValues(processInfo.srcPath):
                    self.logger.info("  add %s" % item)
                    processInfo.srcProduct.addFile(item)


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

            processInfo.destProduct.setNamingConventionEoInstance(namingConventionSip)
            
            self.logger.info(" Eo-Sip product created")
            processInfo.addLog(" Eo-Sip product created")

 
        #
        # Override
        #   do nothing
        #
        def verifySourceProduct(self, processInfo):
                pass


            
        #
        # Override
        #   do nothing
        #
        def prepareProducts(self,processInfo):
                pass
                #processInfo.addLog(" prepare product in:%s" % (processInfo.workFolder))
                #self.logger.info(" prepare product");
                
                #print " #### copy src file '%s' into '%s'" % (processInfo.srcProduct.path, "%s/%s" % (processInfo.workFolder, processInfo.srcProduct.origName))
                #shutil.copyfile(processInfo.srcProduct.path, "%s/%s" % (processInfo.workFolder, processInfo.srcProduct.origName))
                
                #processInfo.addLog("  extracted inside:%s" % (processInfo.workFolder))
                #self.logger.info("  extracted inside:%s" % (processInfo.workFolder))


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

                # set the source EoSip file as pieces in the destination EoSip
                # this is to use directly the source files ( and not what is in the working folder)
                # (kink of having a flag + a path)

                fh=fileHelper()
                for item in processInfo.srcProduct.contentList:
                        print " SET SOURCE FILE:%s as EoSip piece" % item
                        piece = eosip_product.EoPiece(item)
                        piece.localPath=item
                        piece.alias=fh.basename(item)
                        processInfo.destProduct.addPiece(piece)


                
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


        #
        # Override
        #
        # process the list of products
        #
        def processProductsFromInfoKeeper(self):
                global num_total,num_done,num_error,list_done,list_error,description_error
                #
                num=0
                num_total=0
                num_done=0
                num_error=0
                list_done=[]
                list_error=[]
                self.runStartTime=time.time()
                num_all=len(self.productList)

                # create index: use default header, + added if defined
                if self.create_index:
                    self.indexCreator=indexCreator.IndexCreator(None, index_added)
                    self.logger.info("will create index")

                # create shopcart:
                if self.create_shopcart:
                    self.shopcartCreator=shopcartCreator.ShopcartCreator(None, None)
                    self.logger.info("will create shopcart")

                #  create thumbnail:
                if self.create_thumbnail:
                    self.logger.info("will create thumbnail")

                self.statsUtil.start(len(self.productList))


                # for every cycle key, do a EoSIp
                for key in self.keeperFiles.getKeys():
                        self.logger.info("doing products for cycle:%s" % key)

                        
                        aProcessInfo=processInfo.processInfo()
                        aProcessInfo.srcPath=key
                        aProcessInfo.num=num
                        # set some usefull flags in processInfo
                        self.setProcessInfo(aProcessInfo)
                        
                        self.num=self.num+1
                        self.num_total=self.num_total+1
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("")
                        self.logger.info("doing cycle[%d/%d][%s/%s]:%s" % ( num, num_all, num_done, num_error, key))
                        aProcessInfo.addLog("\n\nDoing cycle[%d/%d][%s/%s]:%s" % ( num, num_all, num_done, num_error, key))
                        try:
                                print "### do one cycle:%s" % key
                                self.doOneProduct(aProcessInfo)

                                self.num_done=self.num_done+1
                                self.list_done.append(key+"|"+aProcessInfo.workFolder)

                                # apercu report
                                self.reportToApercu(aProcessInfo, "NAME=EoSip-converter&BINDING=converter:ingester&all=%s&done=%s&total=%s&error=%s&endTime=%s" % (num_all, num_done, num_total, num_error, urllib.quote(self.statsUtil.getEndDate())))

                                if self.create_index:
                                    try:
                                        if len(aProcessInfo.destProduct.browse_metadata_dict)>0: # there is at least one browse
                                            firstBrowsePath=aProcessInfo.destProduct.browse_metadata_dict.iterkeys().next()
                                            self.indexCreator.addOneProduct(aProcessInfo.destProduct.metadata, aProcessInfo.destProduct.browse_metadata_dict[firstBrowsePath])
                                        else:
                                            self.indexCreator.addOneProduct(aProcessInfo.destProduct.metadata, None)
                                    except Exception, e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " ERROR creating index:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                        aProcessInfo.addLog("ERROR creating index:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                        self.logger.error("ERROR creating index: %s  %s" % (exc_type, exc_obj))
                                        pass

                                if self.create_shopcart:
                                    try:
                                        #self.shopcartCreator.debug=1
                                        if len(aProcessInfo.destProduct.browse_metadata_dict)>0: # there is at least one browse
                                            firstBrowsePath=aProcessInfo.destProduct.browse_metadata_dict.iterkeys().next()
                                            self.shopcartCreator.addOneProduct(aProcessInfo.destProduct.metadata, aProcessInfo.destProduct.browse_metadata_dict[firstBrowsePath])
                                        else:
                                            self.shopcartCreator.addOneProduct(aProcessInfo.destProduct.metadata, None)
                                    except Exception, e:
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " ERROR creating shopcart:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                        aProcessInfo.addLog("ERROR creating shopcart:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                        self.logger.error("ERROR creating shopcart: %s  %s" % (exc_type, exc_obj))
                                        pass


                                # write log
                                try:
                                        prodLogPath="%s/conversion_%d.log" % (aProcessInfo.workFolder, num_error)
                                        fd=open(prodLogPath, 'w')
                                        fd.write(aProcessInfo.prodLog)
                                        fd.close()
                                except Exception, eee:
                                        print "Error: problem writing convertion log in fodler:%s" % aProcessInfo.workFolder
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())

                                # save the pinfo in workfolder
                                try:
                                    self.saveProcessInfo(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving processInfo file")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving processInfo file:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                    
                                # save the matadata file in workfolder
                                try:
                                    self.saveMetadata(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving metadata files")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving metadata files:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())



                                
                        except Exception, e:
                                num_error=num_error+1
                                list_error.append("%s|%s" % (key,aProcessInfo.workFolder))
                                exc_type, exc_obj, exc_tb = sys.exc_info()

                                # apercu report
                                self.reportToApercu(aProcessInfo, "NAME=EoSip-converter&BINDING=converter:ingester&done=%s&total=%s&error=%s&endTime=%s" % (num_done, num_total, num_error, urllib.quote(self.statsUtil.getEndDate())))

                                
                                try:
                                    self.logger.error("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                    aProcessInfo.addLog("Error:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc()))
                                except  Exception, ee:
                                    self.logger.error(" Error: adding log info into processInfo:%s" % aProcessInfo)
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR adding error in log:%s  %s" %  (exc_type, exc_obj)

                                # write log
                                try:
                                        prodLogPath="%s/bad_convertion_%d.log" % (aProcessInfo.workFolder, num_error)
                                        fd=open(prodLogPath, 'w')
                                        fd.write(aProcessInfo.prodLog)
                                        fd.close()
                                except Exception, eee:
                                        print "Error: problem writing convertion log in fodler:%s" % aProcessInfo.workFolder
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print " problem is:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())


                                # save the pinfo in workfolder
                                try:
                                    self.saveProcessInfo(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving processInfo file")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving processInfo file:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())
                                    
                                # save the matadata file in workfolder
                                try:
                                    self.saveMetadata(aProcessInfo)
                                except:
                                    self.logger.error(" Error: saving metadata files")
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print " ERROR saving metadata files:%s  %s%s\n" %  (exc_type, exc_obj, traceback.format_exc())


                        if self.max_product_done!=-1 and num>=self.max_product_done:
                                self.logger.info("max number of product to be done reached:%s; STOPPING" % self.max_product_done)
                                break


                self.runStopTime=time.time()
                tmp=self.summary()
                
                # write convertion log
                if not os.path.exists(self.LOG_FOLDER):
                    os.makedirs(self.LOG_FOLDER)
                path="%s/%s.log" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                fd.write(tmp)
                fd.close()
                print " batch done log '%s' written in:%s" % (self.batchName, path)

                # write keeped info in any
                path="%s/%s_KEEPED.txt" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                fd.write(self.infoKeeper.toString())
                fd.close()
                print " keeped information '%s' written in:%s" % (self.batchName, path)
                
                # write done list
                path="%s/%s_DONE.log" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                for item in list_done:
                    fd.write(item+"\n")
                fd.close()
                path="%s/%s_ERROR.log" % (self.LOG_FOLDER, self.batchName)
                fd=open(path, "w")
                for item in list_error:
                    fd.write(item+"\n")
                fd.close()
                print " batch error log '%s' written in:%s" % (self.batchName, path)
                
                if self.create_index:
                    # index text:
                    tmp=self.indexCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nINDEX:\n%s"  % tmp
                    path="%s/%s" % (self.OUTSPACE, '%s_index.txt' % self.fixed_batch_name)
                    fd=open(path, "w")
                    fd.write(tmp)
                    fd.close()
                    print "\n index written in:%s" % (path)

                if self.create_shopcart!=0:
                    # index text:
                    tmp=self.shopcartCreator.getIndexesText()
                    if self.debug!=0:
                        print "\n\nSHOPCART:\n%s"  % tmp
                    path="%s/%s" % (self.OUTSPACE, '%s_shopcart.txt' % self.fixed_batch_name)
                    fd=open(path, "w")
                    fd.write("%d\n" % self.shopcartCreator.getSize())
                    #fd.write("\n")
                    fd.write(tmp)
                    fd.close()
                    print "\n shopcart written in:%s" % (path)
                

        #
        # process the list of products
        #
        def prepareLists(self):
                global REAPER_PACKAGES, REAPER_PACKAGES_FILES
                #
                self.num=0
                self.num_total=0
                self.num_done=0
                self.num_error=0
                self.list_done=[]
                self.list_error=[]
                self.runStartTime=time.time()
                self.num_all=len(self.productList)


                # create index: use default header, + added if defined
                if self.create_index:
                    self.indexCreator=indexCreator.IndexCreator(None, self.index_added)
                    self.logger.info("will create index")

                # create shopcart:
                if self.create_shopcart:
                    self.shopcartCreator=shopcartCreator.ShopcartCreator(None, None)
                    self.logger.info("will create shopcart")

                #  create thumbnail:
                if self.create_thumbnail:
                    self.logger.info("will create thumbnail")

                self.statsUtil.start(len(self.productList))

                # create the list of eoSip packages to be done
                # pack the products in 3 days cycle by month
                # pack the products in 168 days cycle by month
                # pack the products in 35 days cycle by cycle
                #
                # package files will have name like:
                # - M_yyyymm
                # - C_xxxx
                #
                ers1PhasesCycles=ers1cycles.Ers1PhasesCycles("ERS1")
                ers2PhasesCycles=ers2cycles.Ers2PhasesCycles("ERS2")
                packageFilesDict={}
                keeperPackages = infoKeeper.infoKeeper()
                keeperFiles = infoKeeper.infoKeeper()
                for item in self.productList:
                        name=os.path.basename(item)
                        if self.debug!=0:
                                print "\ndoing filename:%s" % name
                        sat=name[1]
                        start=name.split('_')[6].replace('T', '')
                        
                        if self.debug!=0:
                                print " start:%s" % start
                        if sat=='1':
                                p,c = ers1PhasesCycles.getPhaseAndCycleFromShortTime(start)
                                if self.debug!=0:
                                        print " is in phase:%s and cycle:%s" % (p,c)
                                if p!=None and c!=None:
                                        phase=ers1PhasesCycles.getPhase(p)
                                        if phase.getDuration()==3 or phase.getDuration()==168:
                                                pname="M1_%s" % start[0:6]
                                                keeperPackages.addInfo("M1", pname)
                                        else:
                                                pname="C1_%s" % c
                                                keeperPackages.addInfo("C1", pname)
                                        keeperFiles.addInfo(pname, item)
                                else:
                                       keeperPackages.addInfo("no p or c", "%s %s" % (p,c))
                                       keeperFiles.addInfo("no p or c", item)
                                
                        elif sat=='2':
                                p,c = ers2PhasesCycles.getPhaseAndCycleFromShortTime(start)
                                if self.debug!=0:
                                        print "is in phase:%s and cycle:%s" % (p,c)
                                if p!=None and c!=None:
                                        phase=ers2PhasesCycles.getPhase(p)
                                        if phase.getDuration()==3 or phase.getDuration()==168:
                                                pname="M2_%s" % start[0:6]
                                                keeperPackages.addInfo("M2", pname)
                                        else:
                                                pname="C2_%s" % c
                                                keeperPackages.addInfo("C2", pname)
                                        keeperFiles.addInfo(pname, item)
                                else:
                                       keeperPackages.addInfo("no p or c", "%s %s" % (p,c))
                                       keeperFiles.addInfo("no p or c", item)
                        else:
                                raise Exception("invalid sat:%s" % sat)

                print "\n\nlist of eoSip packages:%s" % keeperPackages.toString()
                fd=open(REAPER_PACKAGES, 'w')
                fd.write(keeperPackages.toString())
                fd.close()
                fd=open(REAPER_PACKAGES_FILES, 'w')
                fd.write(keeperFiles.toString())
                fd.close()

                self.keeperPackages=keeperPackages
                self.keeperFiles=keeperFiles




if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            ingester = ingester_reaper_cycle()
            ingester.startJustReadConfig=True
            # read the config as usual
            ingester.starts(sys.argv)
            # check that we have the listOfProduct file in the arguments
            if ingester.options.productListFile==None:
                    raise Exception("Reaper conversion by cycle require a listOfProduct file")
            # use the list of products
            ingester.setProductsList(ingester.options.productListFile)
            # separate by cycles
            ingester.prepareLists()
            #
            ingester.processProductsFromInfoKeeper()
            

            
        else:
            print "syntax: python ingester_xxx.py -c configuration_file.cfg [-l list_of_product_file]"
            sys.exit(1)
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
