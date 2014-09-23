# -*- coding: cp1252 -*-
#
# this class is a base class for Service
#
#
from abc import ABCMeta, abstractmethod
import os, sys
import logging
import ConfigParser


class Service:
    debug=False
    name=None
    propertieFile=None
    properties=None
    ready=True


    #
    # class init
    #
    def __init__(self, name=None):
        self.name=name
        if self.debug:
            print " create class Service; name=%s" % self.name 


    #
    # init
    #
    # param: p is usually the path of a property file, can be local to ingester './xxx.props' or absolute '/...path.../xxx.props'
    #
    def init(self, p=None, ingester=None):
        if self.debug:
            print "### init class Service with parameter:%s" % (p)
        if p[0:2]=="./":
            p="%s/%s" % (ingester.getConverterHomeDir(), p[2:])
        print " using service property file at path:'%s'" % p
        self.propertieFile=p
        self.loadProperties()


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
        return self.properties[propName]


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

