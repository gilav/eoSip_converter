from sipMessageBuilder import SipMessageBuilder


class alt_ProcessingInformation(SipMessageBuilder):
    
    this_ALT = ["<alt:ProcessingInformation>"]

    REPRESENTATION_ALT = ["<eop:processingMode>@processingMode@</eop:processingMode>",
                      "<alt:groundTrackUncertainty>@groundTrackUncertainty@</alt:groundTrackUncertainty>",
                      "<alt:productContentsType>@productContentsType@</alt:productContentsType>",
                      "<alt:samplingRate>@samplingRate@</alt:samplingRate>"]
