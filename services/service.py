# -*- coding: cp1252 -*-
#
# this class is a base class for Service
#
#
from abc import ABCMeta, abstractmethod
from cStringIO import StringIO
import os, sys
import logging
import ConfigParser


class Service:
    SETTING_DEBUG='DEBUG'
    
    debug=True
    name=None
    propertieFile=None
    properties=None
    ingester=None
    ready=True


    #
    # init simple
    # param: p is a string
    #
    def __init__(self, name=None):
        self.name=name
        if self.debug:
            print " create class Service; name=%s" % self.name 


    #
    # init with ingester + property file
    #
    # param: p is usually the path of a property file, can be local to ingester './xxx.props' or absolute '/...path.../xxx.props'. Can be None
    #        ingester is the ingester instance, is used to get the property file path
    #
    # TODO: leave the ingester load the ressources 
    #
    def init(self, p=None, ingester=None):
        self.ingester=ingester
        if p!=None:
            print "### init class Service with parameter:%s" % (p)
            if p[0:2]=="./":
                p="%s/%s" % (self.ingester.getConverterHomeDir(), p[2:])
            print " using service property file at path:'%s'" % p
            self.propertieFile=p
            self.loadProperties()
        else:
            print "### init class Service with no parameter"



    #
    # load the properties setting file
    #
    def loadProperties(self):
        if self.debug:
            print " load properties in Service '%s' from file:%s" % (self.name, self.propertieFile)
        __config = ConfigParser.RawConfigParser()
        __config.optionxform=str
        __config.read(self.propertieFile)
        self.properties=dict(__config.items("GLOBAL"))
        
    #
    #
    def getproperties(self):
        return self.properties

    #
    # return a property value
    #
    def getProperty(self, propName=None):
        try:
            return self.properties[propName]
        except:
            return None

    #
    #
    #
    def dumpProperty(self):
        out=StringIO()
        print >>out, 'service properties dump:'
        for key in self.properties.keys():
                print >>out, " key:'%s'; value:'%s'" % (key, self.properties[key])

        return out.getvalue()

    #
    # process a request
    #
    @abstractmethod
    def processRequest(self):
        pass

    

if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        s=Service("a=1")
        s.processRequest()
    except Exception, err:
        log.exception('Error from throws():')

