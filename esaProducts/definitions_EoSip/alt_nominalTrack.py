from sipMessageBuilder import SipMessageBuilder


class alt_nominalTrack(SipMessageBuilder):
    
    this = ["<alt:nominalTrack gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</alt:nominalTrack>"]

    REPRESENTATION = ["<eop:multiExtentOf>",
"<gml:MultiCurve gml:id=\"@gmlId@_$$getNextCounter()$$\">",
"<gml:curveMember>",
"<gml:LineString gml:id=\"@gmlId@_$$getNextCounter()$$\">",
"<gml:posList>@coordList@</gml:posList>",
"</gml:LineString >",
"</gml:curveMember>",
"</gml:MultiCurve >",
"</eop:multiExtentOf>"]
