from sipMessageBuilder import SipMessageBuilder


class om_phenomenonTime(SipMessageBuilder):
    
    this = ["<om:phenomenonTime>"]

    REPRESENTATION = ["gml_TimePeriod"]
