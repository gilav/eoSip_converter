from sipMessageBuilder import SipMessageBuilder


class eop_EarthObservationEquipment(SipMessageBuilder):
    
    this = ["<eop:EarthObservationEquipment gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservationEquipment>"]

    this_ALT = ["<alt:EarthObservationEquipment gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</alt:EarthObservationEquipment>"]

    REPRESENTATION = ["eop_platform",
        "eop_instrument",
        "eop_sensor",
        "eop_acquisitionParameters",
        ]
