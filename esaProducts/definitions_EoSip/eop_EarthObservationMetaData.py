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


class eop_EarthObservationMetaData(SipMessageBuilder):
    
    this = ["<eop:EarthObservationMetaData>", "</eop:EarthObservationMetaData>"]

    REPRESENTATION = ["<eop:identifier>@identifier@</eop:identifier>",
                      "<eop:parentIdentifier>@parentIdentifier@</eop:parentIdentifier>",
                      "<eop:acquisitionType>@acquisitionType@</eop:acquisitionType>",
                      "<eop:productType>@productType@</eop:productType>",
                      "<eop:status>@status@</eop:status>",
                      "eop_processing",
                      "<LOCAL_ATTR></LOCAL_ATTR>"]

    FIELDS = ["identifier", "parentIdentifier", "acquisitionType", "productType", "status"]

    MANDATORY = ["identifier", "parentIdentifier", "acquisitionType", "productType", "status"]

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

