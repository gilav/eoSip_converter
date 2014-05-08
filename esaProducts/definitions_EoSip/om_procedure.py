
from sipMessageBuilder import SipMessageBuilder


class om_procedure(SipMessageBuilder):
    
    this = ["<om:procedure>"]

    REPRESENTATION = ["eop_EarthObservationEquipment"]

    REPRESENTATION_ALT = ["alt_EarthObservationEquipment"]

