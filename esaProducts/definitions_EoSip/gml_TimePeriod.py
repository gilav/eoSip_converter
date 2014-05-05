from sipMessageBuilder import SipMessageBuilder


class gml_TimePeriod(SipMessageBuilder):
    
    this = ["<gml:TimePeriod>"]

    REPRESENTATION = [
        "<gml:beginPosition>@beginPositionDate@T@beginPositionTime@Z</gml:beginPosition>",
        "<gml:endPosition>@endPositionDate@T@endPositionTime@Z</gml:endPosition>"]

