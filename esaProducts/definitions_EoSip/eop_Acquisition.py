from sipMessageBuilder import SipMessageBuilder


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

    OPTIONAL = ["<gml:orbitNumber>@orbitNumber@</gml:orbitNumber>"]
