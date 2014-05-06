from sipMessageBuilder import SipMessageBuilder


class eop_ProcessingInformation(SipMessageBuilder):
    
    this = ["<eop:ProcessingInformation>"]

    #this_ALT = ["<alt:ProcessingInformation>"]

    REPRESENTATION = ["<eop:processingCenter>@processingCenter@</eop:processingCenter>",
                      "<eop:processingDate>@processingDate@</eop:processingDate>",
                      "<eop:processingMode>@processingMode@</eop:processingMode>",
                      "<eop:processorName>@processorName@</eop:processorName>",
                      "<eop:processorVersion>@processorVersion@</eop:processorVersion>"]

    #REPRESENTATION_ALT = ["<alt:processingMode>@processingMode@</alt:processingMode>"]
