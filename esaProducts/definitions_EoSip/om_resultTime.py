from sipMessageBuilder import SipMessageBuilder


class om_resultTime(SipMessageBuilder):
    
    this = ["<gml:resultTime>"]

    REPRESENTATION = ["gml_TimeInstant"]
