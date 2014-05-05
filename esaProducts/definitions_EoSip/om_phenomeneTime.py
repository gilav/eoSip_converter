from sipMessageBuilder import SipMessageBuilder


class om_phenomeneTime(SipMessageBuilder):
    
    this = ["<om:phenomeneTime>"]

    REPRESENTATION = ["gml_TimePeriod"]
