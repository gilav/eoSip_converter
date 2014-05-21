from sipMessageBuilder import SipMessageBuilder


class alt_EarthObservationEquipment(SipMessageBuilder):
    
    this = ["<alt:EarthObservationEquipment gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</alt:EarthObservationEquipment>"]


    REPRESENTATION = ["eop_platform",
        "eop_instrument",
        "eop_sensor",
        "eop_acquisitionParameters",
        ]
