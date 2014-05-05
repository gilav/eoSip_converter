from sipMessageBuilder import SipMessageBuilder


class om_result(SipMessageBuilder):
    
    this = ["<om:result>"]

    #this_SAR = ["<om:result>"]

    #this_ALT = ["<om:result>"]

    #this_OPT = ["<om:result>"]

    REPRESENTATION = ["eop_EarthObservationResult"]

    #REPRESENTATION_SAR = ["sar_EarthObservationResult"]

    #REPRESENTATION_ALT = ["alt_EarthObservationResult"]

    #REPRESENTATION_OPT = ["opt_EarthObservationResult"]
