import os,sys,inspect
import logging
#

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)
    #print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% path modified:%s" % sys.pathsys.path

from metadata import Metadata
from definitions_EoSip.sipMessageBuilder import SipMessageBuilder


class om_resultTime(SipMessageBuilder):
    
    this = ["<gml:resultTime>"]

    REPRESENTATION = ["gml_TimeInstant"]

    FIELDS = ["TimeInstant"]

    MANDATORY = ["TimeInstant"];

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

