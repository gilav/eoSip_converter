from sipMessageBuilder import SipMessageBuilder


class eop_EarthObservationEquipment(SipMessageBuilder):
    
    this = ["<eop:EarthObservationEquipment gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationEquipment>"]

    
    REPRESENTATION = ["eop_platform",
        "eop_instrument",
        "eop_sensor",
        "eop_acquisitionParameters",
        ]
