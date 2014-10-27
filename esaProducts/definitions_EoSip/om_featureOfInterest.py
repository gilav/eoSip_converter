from sipMessageBuilder import SipMessageBuilder


class om_featureOfInterest(SipMessageBuilder):
    
    this = ["<om:featureOfInterest>"]

    this_ALT = ["<om:featureOfInterest>"]

    REPRESENTATION = ["eop_Footprint"]

    REPRESENTATION_ALT = ["alt_Footprint"]


    OPTIONAL = ["eop_Footprint", "alt_Footprint"]
