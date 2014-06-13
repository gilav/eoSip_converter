from sipMessageBuilder import SipMessageBuilder


class opt_EarthObservationResult(SipMessageBuilder):
    
    this = ["<opt:EarthObservationResult gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</opt:EarthObservationResult>"]

    REPRESENTATION = [
        "<BROWSES></BROWSES>",
        "eop_product",
        "<opt:cloudCoverPercentage uom='%'>@cloudCoverPercentage@</opt:cloudCoverPercentage>",
        "<opt:cloudCoverPercentageAssessmentConfidence uom='%'>@cloudCoverPercentageAssessmentConfidence@</opt:cloudCoverPercentageAssessmentConfidence>",
        "<opt:cloudCoverPercentageQuotationMode uom='%'>@cloudCoverPercentageQuotationMode@</opt:cloudCoverPercentageQuotationMode>",
        "<opt:snowCoverPercentage uom='%'>@snowCoverPercentage@</opt:snowCoverPercentage>",
        "<opt:snowCoverPercentageAssessmentConfidence uom='%'>@snowCoverPercentageAssessmentConfidence@</opt:snowCoverPercentageAssessmentConfidence>",
        "<opt:snowCoverPercentageQuotationMode uom='%'>@snowCoverPercentageQuotationMode@</opt:snowCoverPercentageQuotationMode>"]

    OPTIONAL = [
        "<opt:cloudCoverPercentageAssessmentConfidence uom='%'>@cloudCoverPercentageAssessmentConfidence@</opt:cloudCoverPercentageAssessmentConfidence>",
        "<opt:cloudCoverPercentageQuotationMode uom='%'>@cloudCoverPercentageQuotationMode@</opt:cloudCoverPercentageQuotationMode>",
        "<opt:snowCoverPercentage uom='%'>@snowCoverPercentage@</opt:snowCoverPercentage>",
        "<opt:snowCoverPercentageAssessmentConfidence uom='%'>@snowCoverPercentageAssessmentConfidence@</opt:snowCoverPercentageAssessmentConfidence>",
        "<opt:snowCoverPercentageQuotationMode uom='%'>@snowCoverPercentageQuotationMode@</opt:snowCoverPercentageQuotationMode>"]

