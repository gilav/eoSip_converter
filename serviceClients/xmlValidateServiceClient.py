# -*- coding: cp1252 -*-
#
# this class is a base class for Service
#
#
from abc import ABCMeta, abstractmethod
import os, sys
import logging

#
SERVICE_XML_VALIDATION="xmlValidate"
# EO_SIP validation schema
SCHEMA_FROM_TYPOLOGY="SCHEMA_MD"
SCHEMA_SIP="ressources/xml_validator"
SCHEMA_BI="ressources/xml_validator/report/IF-ngEO-BrowseReport.xsd"
SCHEMA_MD_OPT="ressources/xml_validator/opt.xsd"
SCHEMA_MD_SAR="ressources/xml_validator/sar.xsd"
SCHEMA_MD_EOP="ressources/xml_validator/eop.xsd"
SCHEMA_MD_ALT="ressources/xml_validator/alt.xsd"
SCHEMA_MD_LMB="ressources/xml_validator/lmb.xsd"

# properties that are known in service configuration file
SETTING_URL_PATTERN="URL_PATTERN"
SETTING_SCHEMA_FROM_TYPOLOGY="SCHEMA_MD"
SETTING_SCHEMA_SIP="SCHEMA_SIP"
SETTING_SCHEMA_BI="SCHEMA_BI"
SETTING_SCHEMA_MD_OPT="SCHEMA_MD_OPT"
SETTING_SCHEMA_MD_SAR="SCHEMA_MD_SAR"
SETTING_SCHEMA_MD_EOP="SCHEMA_MD_EOP"
SETTING_SCHEMA_MD_ALT="SCHEMA_MD_ALT"
SETTING_SCHEMA_MD_LMB="SCHEMA_MD_LMB"


class XmlValidateServiceClient:
    debug=True
    service=None
    urlPattern=None

    #
    # class init
    #
    def __init__(self, processInfo):
        if self.debug:
            print " init class XmlValidateClient"
        self.service = processInfo.ingester.getService(SERVICE_XML_VALIDATION)
        if self.debug:
            print "@@@@@@@@@@@@@@@@ XmlValidateServiceClient: got service xmlValidate:%s" % self.service
        self.urlPattern=self.service.getProperty(SETTING_URL_PATTERN)
        if self.debug:
            print "@@@@@@@@@@@@@@@@ XmlValidateServiceClient: got urlPattern:%s" % self.urlPattern


    #
    # full validation by service
    #
    def useXmlValidateService(self, processInfo, fileType, xmlPath):
        # build correct url + data
        pos = self.urlPattern.index('?')
        url=self.urlPattern[0:pos]
        data=self.urlPattern[pos+1:]
        if self.debug:
            print "############## service params:url=%s; data=%s; xmlPath=%s" % (url, data, xmlPath)
        data=data.replace("@XML_PATH@", xmlPath)
        #
        schemaPath=self.getValidationSchema(processInfo, fileType)
        data=data.replace("@XSD_PATH@", schemaPath)
        self.service.debug=True
        res=self.service.processRequest(url, data)
        if self.debug:
            print "############## service result:%s" % res

        toks = res.split("\n")
        print "############## service res file:%s" % toks[0]
        if not toks[0]==xmlPath:
            raise Exception("strange response from service:"+res)
        if not toks[1]=="!OK!":
            raise Exception("xml validation failed:"+res)


    #
    # retrieve the schema to be used
    #
    def getValidationSchema(self, processInfo, fileType):
        varName="SCHEMA_%s" % (fileType)

        if varName==SCHEMA_FROM_TYPOLOGY:
            if processInfo.destProduct.TYPOLOGY!=None:
                print "TYPOLOGY:%s" % processInfo.destProduct.TYPOLOGY
                varName="%s_%s" % (varName, processInfo.destProduct.TYPOLOGY)
            else:
                print "TYPOLOGY is None"
        print "get schema from varName:%s" % varName
        path="%s/%s" % (processInfo.ingester.getConverterHomeDir(), globals()[varName])
        return path.replace('\\', '/')


