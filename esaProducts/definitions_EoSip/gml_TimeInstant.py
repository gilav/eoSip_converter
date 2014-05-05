from sipMessageBuilder import SipMessageBuilder


class gml_TimeInstant(SipMessageBuilder):
    
    this = ["<gml:TimeInstant gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</gml:TimeInstant>"]

    REPRESENTATION = ["<gml:timePosition>@timePosition@</gml:timePosition>"]
