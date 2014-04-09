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


class opt_EarthObservationResult(SipMessageBuilder):
    
    this = ["<opt:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</opt:EarthObservationResult>"]

    REPRESENTATION = ["<eop:product>",
        "<eop:ProductInformation>",
        "<eop:fileName>",
        "<ows:ServiceReference xlink:href='@href@'>",
        "<ows:RequestMessage></ows:RequestMessage>",
        "</ows:ServiceReference>",
        "</eop:fileName>",
        "<eop:version>SLA</eop:version>",
        "<eop:size uom='Bytes'>@productSize@</eop:size>",
        "</eop:ProductInformation>",
        "</eop:product>",
        "<opt:cloudCoverPercentage uom='%'>@cloudCoverPercentage@</opt:cloudCoverPercentage>"]

    FIELDS = ["href", "productSize", "cloudCoverPercentage"]

    MANDATORY = ["href", "productSize", "cloudCoverPercentage"]

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

