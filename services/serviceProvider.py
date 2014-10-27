#!/usr/bin/env python
#
# 
# Lavaux Gilles 2014
#
# This class is a service provider
#
#
#
from abc import ABCMeta, abstractmethod
import os,sys,inspect
import traceback


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
try:
    sys.path.index(currentdir)
except:
    sys.path.insert(0,currentdir)
import ConfigParser


class ServiceProvider():
    initString=None
    services=None


    #
    debug=1


    #
    # initString is like: xmlValidate=class@module@properties|parameterString
    # - xmlValidate: name of the service
    # - class@module@properties needed to instanciate the service class
    # - parameterString
    #
    def __init__(self, init):
        print "init ServiceProvider with init string:'%s'" % init
        self.initString = init
        self.services={}


    #
    # add a service
    #
    def addService(self, name, settings, ingester):
        print "add Service with settings string:'%s'" % settings
        
        toks=settings.split("|")
        if len(toks[0].split("@"))!= 3:
            raise Exception("token 1 of service source has not 3 '@' separated fields:'%s'" % toks[1])
            
        aClass,aPackage,setting=toks[0].split("@")
        if self.debug!=0: 
            print "  will instanciate class:'%s' in package:'%s' with init:'%s'" % (aClass,aPackage,setting)
 
        parameters=toks[1]
        if self.debug!=0:
            print " parameters:'%s'" % (parameters)

        # create it:
        module = __import__(aPackage)
        if self.debug!=0:
            print " module loaded:%s" % module
        class_ = getattr(module, aClass)
        aclass = class_(name)
        if self.debug!=0:
            print " got class"
        aclass.init(parameters, ingester);
        self.services[name]=aclass
        if 0==0:
            print " service ready:"
            print aclass.dumpProperty()



    #
    # list the known service
    #
    def listServices(self):
        return self.services.keys()
        

    #
    # get a service
    #
    def getService(self, name):
        if not self.services.has_key(name):
            raise Exception("unknown service name:%s" % name)
        return self.services[name]



        
if __name__ == '__main__':
    try:
        serviceprovider = ServiceProvider("")
        serviceprovider.addService("httpCall", "HttpCall@httpService@None|http://127.0.0.1:7000/validate?XML_PATH=@XML_PATH@&XSD_PATH=@XSD_PATH@")
        
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
