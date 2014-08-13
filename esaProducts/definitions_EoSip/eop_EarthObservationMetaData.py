from sipMessageBuilder import SipMessageBuilder


class eop_EarthObservationMetaData(SipMessageBuilder):
    
    this = ["<eop:EarthObservationMetaData>", "</eop:EarthObservationMetaData>"]

    REPRESENTATION = ["<eop:identifier>@identifier@</eop:identifier>",
                      "<eop:parentIdentifier>@parentIdentifier@</eop:parentIdentifier>",
                      "<eop:acquisitionType>@acquisitionType@</eop:acquisitionType>",
                      "<eop:productType>@productType@</eop:productType>",
                      "<eop:status>@status@</eop:status>",
                      "eop_downlinkedTo",
                      "eop_processing",
                      "<LOCAL_ATTR></LOCAL_ATTR>"]


    #CONDITIONS = {"eop_downlinkedTo":"FILLED__acquisitionStation"}
