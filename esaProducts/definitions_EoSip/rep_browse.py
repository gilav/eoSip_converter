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


class rep_browse(SipMessageBuilder):
    
    this = ["<rep:browse>"]

    REPRESENTATION = ["<rep:browseIdentifier>@browseIdentifier@</rep:browseIdentifier>",
                      "<rep:fileName>@browseFileName@</rep:fileName>",
                      "<rep:imageType>@browseImageType@</rep:imageType>",
                      "<rep:referenceSystemIdentifier>@referenceSystemIdentifier@</rep:referenceSystemIdentifier>",
                      "<BROWSE_CHOICE></BROWSE_CHOICE>",
                      "<rep:startTime>@beginPositionDate@T@beginPositionTime@Z</rep:startTime>",
                      "<rep:endTime>@endPositionDate@T@endPositionTime@Z</rep:endTime>"]

    FIELDS = ['browseIdentifier', 'fileName', 'imageType', 'referenceSystemIdentifier', 'startTime', 'endTime']

    MANDATORY = ['browseIdentifier', 'fileName', 'imageType', 'referenceSystemIdentifier', 'startTime', 'endTime']

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

