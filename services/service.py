# -*- coding: cp1252 -*-
#
# this class is a base class for Service
#
#
from abc import ABCMeta, abstractmethod
import os, sys
import logging


class Service:
    debug=True
    properties=None

    #
    #
    #
    def __init__(self):
        if self.debug:
            print " init class Service"


    #
    #
    #
    def init(self, p=None):
        self.properties=p

    #
    #
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

