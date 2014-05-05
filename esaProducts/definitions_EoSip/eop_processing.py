from sipMessageBuilder import SipMessageBuilder


class eop_processing(SipMessageBuilder):
    
    this = ["<eop:processing>"]

    this_ALT = ["<eop:processing>"]

    REPRESENTATION = ["eop_ProcessingInformation"]

    REPRESENTATION_ALT = ["alt_ProcessingInformation"]

