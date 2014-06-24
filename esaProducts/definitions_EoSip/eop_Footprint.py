from sipMessageBuilder import SipMessageBuilder


class eop_Footprint(SipMessageBuilder):
    
    this = ["<eop:Footprint gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:Footprint>"]

    REPRESENTATION = ["<eop:multiExtentOf>",
"<gml:MultiSurface gml:id=\"@gmlId@_$$getNextCounter()$$\">",
"<gml:surfaceMember>",
"<gml:Polygon gml:id=\"@gmlId@_$$getNextCounter()$$\">",
"<gml:exterior>",
"<gml:LinearRing>",
"<gml:posList>@coordList@</gml:posList>",
"</gml:LinearRing>",
"</gml:exterior>",
"</gml:Polygon>",
"</gml:surfaceMember>",
"</gml:MultiSurface>",
"</eop:multiExtentOf>",
"eop_centerOf"]
