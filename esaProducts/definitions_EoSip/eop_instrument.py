from sipMessageBuilder import SipMessageBuilder


class eop_instrument(SipMessageBuilder):
    
    this = ["<eop:instrument>", "</eop:instrument>"]

    this_ALT = ["<alt:instrument>", "</alt:instrument>"]

    REPRESENTATION = ["<eop:Instrument>",
		      "<eop:shortName>@instrumentShortName@</eop:shortName>",
                      "<eop:description>@instrumentDescription@</eop:description>",
                      "</eop:Instrument>"]

    REPRESENTATION_ALT = ["<eop:Instrument>",
		      "<eop:shortName>@instrumentShortName@</eop:shortName>",
                      "<eop:description>@instrumentDescription@</eop:description>",
                      "</eop:Instrument>"]
