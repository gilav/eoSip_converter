# -*- coding: cp1252 -*-
#
# this class implement access to an http WFS service
#
#
from abc import ABCMeta, abstractmethod
import os, sys
import logging

#
SERVICE_WFS="wfs"
# 

# properties that are known in service configuration file
SETTING_URL_PATTERN="URL_PATTERN"
SETTING_LAYER="LAYER"

class WfsServiceClient:
    debug=True
    service=None
    urlPattern=None
    layer=None

    #
    # class init
    #
    def __init__(self, processInfo):
        if self.debug:
            print " init class WfsServiceClient"
        self.service = processInfo.ingester.getService(SERVICE_WFS)
        if self.debug:
            print "@@@@@@@@@@@@@@@@ WfsServiceClient: got service wms:%s" % self.service
        self.urlPattern=self.service.getProperty(SETTING_URL_PATTERN)
        if self.debug:
            print "@@@@@@@@@@@@@@@@ WfsServiceClient: got urlPattern:%s" % self.urlPattern
        self.layer=self.service.getProperty(SETTING_LAYER)
        if self.debug:
            print "@@@@@@@@@@@@@@@@ WfsServiceClient: got layer name:%s" % self.layer


    #
    # query a WFS server
    #
    def callWfsService(self, processInfo, params):
        # url to be completed will be like: wfs?VERSION=1.1.1&SERVICE=WMS&REQUEST=GetFeatureInfo&FORMAT=image%2Fpng&STYLES=default&SRS=EPSG%3A4326&WIDTH=200&HEIGHT=200&TRANSPARENT=TRUE&BGCOLOR=0xffffff&

        if len(params)!=4:
            raise Exception("params has to be list of 4 coords:  minLon, minLat, maxLon, maxLat")
        
        minLon=params[0]
        minLat=params[1]
        maxLon=params[2]
        maxLat=params[3]
        fullUrl="%sLAYER=%s&QUERY_LAYERS=%s&BBOX=%s%2c%s%2c%s%2c%s" % (self.urlPattern, self.layer, self.layer, minLon, minLat, maxLon, maxLat)
        # build correct url + data
        pos = fullUrl.index('?')
        url=fullUrl[0:pos]
        params=fullUrl[pos+1:]
        if self.debug:
            print "############## service params:url=%s; params=%s" % (url, params)
        #
        self.service.debug=True
        res=self.service.processRequest(url, params, False) # dont use post
        if self.debug:
            print "############## service result:%s" % res

        return res


