from sipMessageBuilder import SipMessageBuilder


class eop_ProcessingInformation(SipMessageBuilder):
    
    this = ["<eop:ProcessingInformation>"]

    #this_ALT = ["<alt:ProcessingInformation>"]

    REPRESENTATION = ["<eop:processingMode>@processingMode@</eop:processingMode>"]

    #REPRESENTATION_ALT = ["<alt:processingMode>@processingMode@</alt:processingMode>"]
