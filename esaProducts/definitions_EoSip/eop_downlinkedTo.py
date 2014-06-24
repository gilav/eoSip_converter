from sipMessageBuilder import SipMessageBuilder


class eop_downlinkedTo(SipMessageBuilder):
    
    this = ["<eop:downlinkedTo>"]

    REPRESENTATION = ["<eop:DownlinkInformation>",
                      "<eop:acquisitionStation>@acquisitionStation@</eop:acquisitionStation>",
                      "<eop:acquisitionDate>@acquisitionDate@</eop:acquisitionDate>",
                      "</eop:DownlinkInformation>"]


    OPTIONAL = ["<eop:acquisitionDate>@acquisitionDate@</eop:acquisitionDate>"]
