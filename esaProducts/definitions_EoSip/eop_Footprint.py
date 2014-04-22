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


class eop_Footprint(SipMessageBuilder):
    
    this = ["<eop:Footprint gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:Footprint>"]

    REPRESENTATION = ["<eop:multiExtentOf>",
"<gml:MultiSurface gml:id=\"@gmlId@_$$getNextCounter()$$\">",
"<gml:surfaceMember>",
"<gml:Polygon gml:id=\"@gmlId@_$$getNextCounter()$$\">",
"<gml:exterior>",
"<gml:LinearRing>",
"<gml:posList>@coordList@</gml:posList>",
"</gml:LinearRing>",
"</gml:exterior>",
"</gml:Polygon>",
"</gml:surfaceMember>",
"</gml:MultiSurface>",
"</eop:multiExtentOf>"]

    FIELDS = ["gmlId", "coordList"]

    MANDATORY = ["gmlId", "coordList"]

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

