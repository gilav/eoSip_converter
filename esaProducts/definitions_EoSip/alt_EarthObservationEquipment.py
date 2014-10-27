from sipMessageBuilder import SipMessageBuilder


class alt_EarthObservationEquipment(SipMessageBuilder):
    
    this = ["<alt:EarthObservationEquipment gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</alt:EarthObservationEquipment>"]


    REPRESENTATION = [
        "eop_instrument",
        "alt_platform"
        ]
