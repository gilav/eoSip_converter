from sipMessageBuilder import SipMessageBuilder


class alt_Acquisition(SipMessageBuilder):
    
    this = ["<alt:Acquisition>"]

    REPRESENTATION = [
        "<eop:orbitNumber>@orbitNumber@</eop:orbitNumber>",
        "<eop:lastOrbitNumber>@lastOrbitNumber@</eop:lastOrbitNumber>",
        "<eop:orbitDirection>@orbitDirection@</eop:orbitDirection>",
        "<eop:wrsLongitudeGrid codeSpace=\"\">@wrsLongitudeGrid@</eop:wrsLongitudeGrid>",
        "<eop:wrsLatitudeGrid codeSpace=\"\">@wrsLatitudeGrid@</eop:wrsLatitudeGrid>",
        "<eop:illuminationAzimuthAngle uom=\"degrees\">@illuminationAzimuthAngle@</eop:illuminationAzimuthAngle>",
        "<eop:illuminationZenithAngle uom=\"degrees\">@illuminationZenithAngle@</eop:illuminationZenithAngle>",
        "<eop:illuminationElevationAngle uom=\"degrees\">@illuminationElevationAngle@</eop:illuminationElevationAngle>",
        "<eop:incidenceAngle uom=\"degrees\">@incidenceAngle@</eop:incidenceAngle>",
        "<eop:instrumentZenithAngle uom=\"degrees\">@instrumentZenithAngle@</eop:instrumentZenithAngle>",
        "<eop:instrumentElevationAngle uom=\"degrees\">@instrumentElevationAngle@</eop:instrumentElevationAngle>",
        "<alt:cycleNumber>@cycleNumber@</alt:cycleNumber>",
        "<alt:isSegment>@isSegment@</alt:isSegment>",
        "<alt:relativePassNumber>@relativePassNumber@</alt:relativePassNumber>"]

    OPTIONAL = ["<eop:lastOrbitNumber>@lastOrbitNumber@</eop:lastOrbitNumber>",
                "<eop:wrsLongitudeGrid codeSpace=\"\">@wrsLongitudeGrid@</eop:wrsLongitudeGrid>",
                "<eop:wrsLatitudeGrid codeSpace=\"\">@wrsLatitudeGrid@</eop:wrsLatitudeGrid>",
                "<eop:illuminationAzimuthAngle uom=\"degrees\">@illuminationAzimuthAngle@</eop:illuminationAzimuthAngle>",
                "<eop:illuminationZenithAngle uom=\"degrees\">@illuminationZenithAngle@</eop:illuminationZenithAngle>",
                "<eop:illuminationElevationAngle uom=\"degrees\">@illuminationElevationAngle@</eop:illuminationElevationAngle>",
                "<eop:incidenceAngle uom=\"degrees\">@incidenceAngle@</eop:incidenceAngle>",
                "<eop:instrumentZenithAngle uom=\"degrees\">@instrumentZenithAngle@</eop:instrumentZenithAngle>",
                "<eop:instrumentElevationAngle uom=\"degrees\">@instrumentElevationAngle@</eop:instrumentElevationAngle>",
                "<alt:cycleNumber>@cycleNumber@</alt:cycleNumber>",
                "<alt:isSegment>@isSegment@</alt:isSegment>",
                "<alt:relativePassNumber>@relativePassNumber@</alt:relativePassNumber>"]
