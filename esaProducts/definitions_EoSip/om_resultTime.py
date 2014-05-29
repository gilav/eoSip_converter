from sipMessageBuilder import SipMessageBuilder


class om_resultTime(SipMessageBuilder):
    
    this = ["<om:resultTime>"]

    REPRESENTATION = ["gml_TimeInstant"]
