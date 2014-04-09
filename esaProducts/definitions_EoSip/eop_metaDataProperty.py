import os,sys,inspect
import logging
#

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)

from metadata import Metadata
from definitions_EoSip.sipMessageBuilder import SipMessageBuilder


class eop_metaDataProperty(SipMessageBuilder):
    
    this = ["<eop:metaDataProperty>", "</eop:metaDataProperty>"]

    REPRESENTATION = ["eop_EarthObservationMetaData"]

    FIELDS = []

    MANDATORY = []

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

