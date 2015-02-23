# -*- coding: cp1252 -*-
#
# factory for naming conventions
#

import os, sys, inspect
import logging
from product import Product
import metadata
import formatUtils
from cStringIO import StringIO
#
# supported naming conventions
#
#from namingConvention import NamingConvention
#from namingConvention_aeolus import NamingConvention_Aeolus


class NamingConventionFactory():
    #
    supportedNamingPackagesMap={'NamingConvention':'namingConvention','NamingConvention_Aeolus':'namingConvention_aeolus'}
    
    #
    debug=1

    #
    # init
    #
    def __init__(self):
        print "init NamingConventionFactory"


    #
    # return list of supported naming
    #
    def getSupportedNaming(self):
        #res=[]
        #for item in self.supportedNamingPackagesMap:
        #    pos = item.find('@')
        #    res.append(item[0:pos])
        #return res
        return self.supportedNamingPackagesMap.keys()


    #
    # return 
    #
    def getNamingPackageName(self, className):
        if not self.supportedNamingPackagesMap.has_key(className):
            raise Exception("naming name not supported:%s" % className)
        return self.supportedNamingPackagesMap[className]
    

    #
    # return naming instance from packageName
    #
    def getNamingInstance(self, namingClass):
        # build the class instance from package/class name
        namingPackage=self.getNamingPackageName(namingClass)
        module = __import__(namingPackage)
        class_ = getattr(module, namingClass)
        instance = class_()
        print " got instance of: %s.%s" % (namingPackage, namingClass)
        return instance

    #
    # return the possible instances pattern for a given namingConvention
    # naming: name of the naming convention package
    #
    def getPossibleInstancePatternsFromName(self,namingClass):
        return self.getPossibleInstancePatterns(self.getNamingPackageName(namingClass), namingClass)
        

    #
    # return the possible instances pattern for a given namingConvention
    # naming: name of the naming convention package
    #
    def getPossibleInstancePatterns(self, namingPackage, namingClass):
        # build the class instance from package/class name
        module = __import__(namingPackage)
        class_ = getattr(module, namingClass)
        instance = class_()
        
        if self.debug!=0:
            print " got instance of: %s.%s" % (namingPackage, namingClass)

        return instance.possible_pattern


    #
    #
    #
    def findNamingUsed(self, filename):
        # test againg every known pattern
        print "\n\n\n find naming of filename:%s" % filename
        for naming in factory.getSupportedNaming():
            print "\n\n  test vs naming:%s" % naming
            instance=self.getNamingInstance(naming)
            possiblesPattern=instance.possible_pattern
            if debug != 0:
                n=0
                for item in possiblesPattern:
                    print "  possiblesPattern[%s]:%s" % (n,item)
                    n=n+1
            print "\n\n"
            match = instance.guessPatternUsed(filename, possiblesPattern)
            n=0
            for item in match:
                print "  ##### match[%s]:%s" %(n,item)
                n=n+1
            
            

    #
    #
    #
    def setDebug(self, d):
        self.debug=d



if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        factory = NamingConventionFactory()
        instances = factory.getPossibleInstancePatterns('namingConvention', 'NamingConvention')

        #
        print " supported naming: %s" %  factory.getSupportedNaming()

        #
        print " possible instances pattern:"
        for item in instances:
             print "  - %s" % item

        #
        filename='SP1_OPER_HRV__X__1A_19970514T100045_19970514T100054_000312_0075_0259.SIP.ZIP'
        factory.findNamingUsed(filename)

             

        
            
    except Exception, err:
        log.exception('Error from throws():')

