from sipMessageBuilder import SipMessageBuilder


class eop_Instrument(SipMessageBuilder):
    
    this = ["<eop:Instrument>", "</eop:Instrument>"]


    REPRESENTATION = ["<eop:shortName>@instrumentShortName@</eop:shortName>",
                      "<eop:description>@instrumentDescription@</eop:description>"]


    OPTIONAL = ["<eop:shortName>@instrumentShortName@</eop:shortName>",
                "<eop:description>@instrumentDescription@</eop:description>"]
