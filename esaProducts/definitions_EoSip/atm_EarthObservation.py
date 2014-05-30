from sipMessageBuilder import SipMessageBuilder


class atm_EarthObservation(SipMessageBuilder):
    
    this = ["atm:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</atm:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomenonTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]


