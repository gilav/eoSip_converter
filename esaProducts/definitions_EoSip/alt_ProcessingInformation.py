from sipMessageBuilder import SipMessageBuilder


class alt_ProcessingInformation(SipMessageBuilder):
    
    this_ALT = ["<alt:ProcessingInformation>"]

    REPRESENTATION_ALT = ["<eop:processingCenter>@processingCenter@</eop:processingCenter>",
                      "<eop:processingDate>@processingDate@</eop:processingDate>",
                      "<eop:processorName>@processorName@</eop:processorName>",
                      "<eop:processorVersion>@processorVersion@</eop:processorVersion>",
                      "<eop:processingLevel>@processingLevel@</eop:processingLevel>",
                      "<eop:nativeProductFormat>@nativeProductFormat@</eop:nativeProductFormat>",
                      "<eop:processingMode>@processingMode@</eop:processingMode>"]

    OPTIONAL = ["<eop:processingCenter>@processingCenter@</eop:processingCenter>",
                      "<eop:processingDate>@processingDate@</eop:processingDate>",
                      "<eop:processorName>@processorName@</eop:processorName>",
                      "<eop:processorVersion>@processorVersion@</eop:processorVersion>",
                      "<eop:processingLevel>@processingLevel@</eop:processingLevel>",
                      "<eop:nativeProductFormat>@nativeProductFormat@</eop:nativeProductFormat>",
                      "<eop:processingMode>@processingMode@</eop:processingMode>"]
