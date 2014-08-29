from sipMessageBuilder import SipMessageBuilder


class eop_ProcessingInformation(SipMessageBuilder):
    
    this = ["<eop:ProcessingInformation>"]


    REPRESENTATION = ["<eop:processingCenter codeSpace=\"\">@processingCenter@</eop:processingCenter>",
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
