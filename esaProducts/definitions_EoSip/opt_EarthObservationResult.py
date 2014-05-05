from sipMessageBuilder import SipMessageBuilder


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

