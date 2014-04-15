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


class eop_Acquisition(SipMessageBuilder):
    
    this = ["<eop:Acquisition>"]

    REPRESENTATION = [
        "<gml:orbitNumber>@orbitNumber@</gml:orbitNumber>",
        "<gml:orbitDirection>@orbitDirection@</gml:orbitDirection>",
        "<gml:wrsLongitudeGrid>@wrsLongitudeGrid@</gml:wrsLongitudeGrid>",
        "<gml:wrsLatitudeGrid>@wrsLatitudeGrid@</gml:wrsLatitudeGrid>",
        "<gml:illuminationAzimuthAngle>@illuminationAzimuthAngle@</gml:illuminationAzimuthAngle>",
        "<gml:illuminationZenithAngle>@illuminationZenithAngle@</gml:illuminationZenithAngle>",
        "<gml:illuminationElevationAngle>@illuminationElevationAngle@</gml:illuminationElevationAngle>",
        "<gml:incidanceAngle>@incidanceAngle@</gml:incidanceAngle>",
        "<eop:instrumentZenithAngle>@instrumentZenithAngle@</eop:instrumentZenithAngle>",
        "<eop:instrumentElevationAngle>@instrumentElevationAngle@</eop:instrumentElevationAngle>"]

    FIELDS = ["orbitNumber", "orbitDirection" ,"wrsLongitudeGrid", "wrsLatitudeGrid", "illuminationAzimuthAngle", "illuminationZenithAngle", "illuminationElevationAngle", "incidanceAngle"]

    MANDATORY = ["orbitNumber", "orbitDirection" ,"wrsLongitudeGrid", "wrsLatitudeGrid", "illuminationAzimuthAngle", "illuminationZenithAngle", "illuminationElevationAngle", "incidanceAngle"]

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)

