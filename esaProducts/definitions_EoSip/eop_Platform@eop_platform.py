from sipMessageBuilder import SipMessageBuilder


class eop_Platform(SipMessageBuilder):
    
    this = ["<eop:Platform>"]

    REPRESENTATION = ["<eop:shortName>@platformShortName@</eop:shortName>",
        "<eop:serialIdentifier>@platformSerialIdentifier@</eop:serialIdentifier>"]
