from sipMessageBuilder import SipMessageBuilder


class opt_EarthObservation(SipMessageBuilder):
    
    this = ["<opt:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</opt:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomeneTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]
