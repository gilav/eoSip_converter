from sipMessageBuilder import SipMessageBuilder


class eop_EarthObservationResult(SipMessageBuilder):
    
    this = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    this_SAR = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    this_ALT = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    this_OPT = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

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
        "</eop:product>"]

    REPRESENTATION_SAR = ["<eop:product>",
        "<eop:ProductInformation>",
        "<eop:fileName>",
        "<ows:ServiceReference xlink:href='@href@'>",
        "<ows:RequestMessage></ows:RequestMessage>",
        "</ows:ServiceReference>",
        "</eop:fileName>",
        "<eop:version>SLA</eop:version>",
        "<eop:size uom='Bytes'>@productSize@</eop:size>",
        "</eop:ProductInformation>",
        "</eop:product>"]

    REPRESENTATION_ALT = ["<eop:product>",
        "<eop:ProductInformation>",
        "<eop:fileName>",
        "<ows:ServiceReference xlink:href='@href@'>",
        "<ows:RequestMessage></ows:RequestMessage>",
        "</ows:ServiceReference>",
        "</eop:fileName>",
        "<eop:version>SLA</eop:version>",
        "<eop:size uom='Bytes'>@productSize@</eop:size>",
        "</eop:ProductInformation>",
        "</eop:product>"]

    REPRESENTATION_OPT = ["<eop:product>",
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
        "<opt:cloudCoverPercentage uom='%'>@cloudCoverPercentage@</opt:cloudCoverPercentage>",
        "<opt:cloudCoverPercentageAssessmentConfidence uom='%'>@cloudCoverPercentageAssessmentConfidence@</opt:cloudCoverPercentageAssessmentConfidence>",
        "<opt:cloudCoverPercentageQuotationMode uom='%'>@cloudCoverPercentageQuotationMode@</opt:cloudCoverPercentageQuotationMode>",
        "<opt:snowCoverPercentage uom='%'>@snowCoverPercentage@</opt:snowCoverPercentage>",
        "<opt:snowCoverPercentageAssessmentConfidence uom='%'>@snowCoverPercentageAssessmentConfidence@</opt:snowCoverPercentageAssessmentConfidence>",
        "<opt:snowCoverPercentageQuotationMode uom='%'>@snowCoverPercentageQuotationMode@</opt:snowCoverPercentageQuotationMode>",
                          ]

