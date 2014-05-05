import os,sys,inspect
import logging
#

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)
    #print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% path modified:%s" % sys.path

from metadata import Metadata
from definitions_EoSip.sipMessageBuilder import SipMessageBuilder


class eop_acquisitionParameters(SipMessageBuilder):
    
    this = ["<eop:acquisitionParameters>"]

    REPRESENTATION = ["eop_Acquisition"]
    REPRESENTATION_SAR = ["sar_Acquisition"]

    FIELDS = ["Acquisition"]

    MANDATORY = ["Acquisition"];

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

