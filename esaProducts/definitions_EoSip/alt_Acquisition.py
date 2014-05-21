from sipMessageBuilder import SipMessageBuilder


class alt_Acquisition(SipMessageBuilder):
    
    this = ["<alt:Acquisition>"]

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
        "<eop:instrumentElevationAngle>@instrumentElevationAngle@</eop:instrumentElevationAngle>",
        "<alt:cycleNumber>@cycleNumber@</alt:cycleNumber>",
        "<alt:isSegment>@isSegment@</alt:isSegment>",
        "<alt:relativePassNumber>@relativePassNumber@</alt:relativePassNumber>"]

    OPTIONAL = ["<gml:orbitNumber>@orbitNumber@</gml:orbitNumber>"]
