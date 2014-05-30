from sipMessageBuilder import SipMessageBuilder


class opt_EarthObservationEquipment(SipMessageBuilder):
    
    this = ["<opt:EarthObservationEquipment gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</opt:EarthObservationEquipment>"]

    
    REPRESENTATION = ["eop_platform",
        "eop_instrument",
        "eop_sensor",
        "eop_acquisitionParameters",
        ]
