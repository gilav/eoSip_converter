from sipMessageBuilder import SipMessageBuilder


class eop_sensor(SipMessageBuilder):
    
    this = ["<eop:sensor>"]

    REPRESENTATION = ["eop_Sensor@eop_sensor"]
