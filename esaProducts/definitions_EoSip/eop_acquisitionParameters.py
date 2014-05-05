from sipMessageBuilder import SipMessageBuilder


class eop_acquisitionParameters(SipMessageBuilder):
    
    this = ["<eop:acquisitionParameters>"]

    REPRESENTATION = ["eop_Acquisition"]
    REPRESENTATION_SAR = ["sar_Acquisition"]
    REPRESENTATION_ALT = ["alt_Acquisition"]
