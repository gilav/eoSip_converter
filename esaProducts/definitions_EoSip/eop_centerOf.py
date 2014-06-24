from sipMessageBuilder import SipMessageBuilder


class eop_centerOf(SipMessageBuilder):
    
    this = ["<eop:centerOf>"]

    REPRESENTATION = ["<gml:Point gml:id=\"@gmlId@_$$getNextCounter()$$\">",
                      "<gml:pos>@sceneCenter@</gml:pos>",
                      "</gml:Point>"]

