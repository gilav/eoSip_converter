from sipMessageBuilder import SipMessageBuilder


class eop_Acquisition(SipMessageBuilder):
    
    this = ["<eop:Acquisition>"]

    REPRESENTATION = [
        "<eop:orbitNumber>@orbitNumber@</eop:orbitNumber>",
        "<eop:lastOrbitNumber>@lastOrbitNumber@</eop:lastOrbitNumber>",
        "<eop:orbitDirection>@orbitDirection@</eop:orbitDirection>",
        "<eop:wrsLongitudeGrid codeSpace=\"\">@wrsLongitudeGrid@</eop:wrsLongitudeGrid>",
        "<eop:wrsLatitudeGrid codeSpace=\"\">@wrsLatitudeGrid@</eop:wrsLatitudeGrid>",
        "<eop:ascendingNodedate>@ascendingNodedate@</eop:ascendingNodedate>",
        "<eop:ascendingNodeLongitude>@ascendingNodeLongitude@</eop:ascendingNodeLongitude>",
        "<eop:startTimeFromAscendingNode>@startTimeFromAscendingNode@</eop:startTimeFromAscendingNode>",
        "<eop:completionTimeFromAscendingNode>@completionTimeFromAscendingNode@</eop:completionTimeFromAscendingNode>",
        "<eop:illuminationAzimuthAngle uom=\"degrees\">@illuminationAzimuthAngle@</eop:illuminationAzimuthAngle>",
        "<eop:illuminationZenithAngle uom=\"degrees\">@illuminationZenithAngle@</eop:illuminationZenithAngle>",
        "<eop:illuminationElevationAngle uom=\"degrees\">@illuminationElevationAngle@</eop:illuminationElevationAngle>",
        "<eop:instrumentAzimuthAngle uom=\"degrees\">@instrumentAzimuthAngle@</eop:instrumentAzimuthAngle>",
        "<eop:instrumentZenithAngle uom=\"degrees\">@instrumentZenithAngle@</eop:instrumentZenithAngle>",
        "<eop:instrumentElevationAngle uom=\"degrees\">@instrumentElevationAngle@</eop:instrumentElevationAngle>",
        "<eop:incidenceAngle uom=\"degrees\">@incidenceAngle@</eop:incidenceAngle>",
        "<eop:alongTrackIncidenceAngle uom=\"degrees\">@alongTrackIncidenceAngle@</eop:alongTrackIncidenceAngle>",
        "<eop:acrossTrackIncidenceAngle uom=\"degrees\">@acrossTrackIncidenceAngle@</eop:acrossTrackIncidenceAngle>",
        "<eop:pitch uom=\"degrees\">@pitch@</eop:pitch>",
        "<eop:roll uom=\"degrees\">@roll@</eop:roll>",
        "<eop:yaw uom=\"degrees\">@yaw@</eop:yaw>"]



    OPTIONAL = [
        "<eop:lastOrbitNumber>@lastOrbitNumber@</eop:lastOrbitNumber>",
        "<eop:wrsLongitudeGrid codeSpace=\"\">@wrsLongitudeGrid@</eop:wrsLongitudeGrid>",
        "<eop:wrsLatitudeGrid codeSpace=\"\">@wrsLatitudeGrid@</eop:wrsLatitudeGrid>",
        "<eop:ascendingNodedate>@ascendingNodedate@</eop:ascendingNodedate>",
        "<eop:ascendingNodeLongitude>@ascendingNodeLongitude@</eop:ascendingNodeLongitude>",
        "<eop:startTimeFromAscendingNode>@startTimeFromAscendingNode@</eop:startTimeFromAscendingNode>",
        "<eop:completionTimeFromAscendingNode>@completionTimeFromAscendingNode@</eop:completionTimeFromAscendingNode>",
        "<eop:illuminationAzimuthAngle uom=\"degrees\">@illuminationAzimuthAngle@</eop:illuminationAzimuthAngle>",
        "<eop:illuminationZenithAngle uom=\"degrees\">@illuminationZenithAngle@</eop:illuminationZenithAngle>",
        "<eop:illuminationElevationAngle uom=\"degrees\">@illuminationElevationAngle@</eop:illuminationElevationAngle>",
        "<eop:instrumentAzimuthAngle uom=\"degrees\">@instrumentAzimuthAngle@</eop:instrumentAzimuthAngle>",
        "<eop:instrumentZenithAngle uom=\"degrees\">@instrumentZenithAngle@</eop:instrumentZenithAngle>",
        "<eop:instrumentElevationAngle uom=\"degrees\">@instrumentElevationAngle@</eop:instrumentElevationAngle>",
        "<eop:incidenceAngle uom=\"degrees\">@incidenceAngle@</eop:incidenceAngle>",
        "<eop:alongTrackIncidenceAngle uom=\"degrees\">@alongTrackIncidenceAngle@</eop:alongTrackIncidenceAngle>",
        "<eop:acrossTrackIncidenceAngle uom=\"degrees\">@acrossTrackIncidenceAngle@</eop:acrossTrackIncidenceAngle>",
        "<eop:pitch uom=\"degrees\">@pitch@</eop:pitch>",
        "<eop:roll uom=\"degrees\">@roll@</eop:roll>",
        "<eop:yaw uom=\"degrees\">@yaw@</eop:yaw>"]
