from sipMessageBuilder import SipMessageBuilder


class alt_EarthObservation(SipMessageBuilder):
    
    this = ["<alt:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</alt:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomeneTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]


