from sipMessageBuilder import SipMessageBuilder


class eop_EarthObservationResult(SipMessageBuilder):
    
    this = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    #this_SAR = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    #this_ALT = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    #this_OPT = ["<eop:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationResult>"]

    REPRESENTATION = ["<BROWSES></BROWSES>",
                      "eop_product"]

    #REPRESENTATION_SAR = ["eop_product"]

    #REPRESENTATION_ALT = ["eop_product"]

    #REPRESENTATION_OPT = ["eop_product",
    #    "<opt:cloudCoverPercentage uom='%'>@cloudCoverPercentage@</opt:cloudCoverPercentage>",
    #    "<opt:cloudCoverPercentageAssessmentConfidence uom='%'>@cloudCoverPercentageAssessmentConfidence@</opt:cloudCoverPercentageAssessmentConfidence>",
    #    "<opt:cloudCoverPercentageQuotationMode uom='%'>@cloudCoverPercentageQuotationMode@</opt:cloudCoverPercentageQuotationMode>",
    #    "<opt:snowCoverPercentage uom='%'>@snowCoverPercentage@</opt:snowCoverPercentage>",
    #    "<opt:snowCoverPercentageAssessmentConfidence uom='%'>@snowCoverPercentageAssessmentConfidence@</opt:snowCoverPercentageAssessmentConfidence>",
    #    "<opt:snowCoverPercentageQuotationMode uom='%'>@snowCoverPercentageQuotationMode@</opt:snowCoverPercentageQuotationMode>"]

