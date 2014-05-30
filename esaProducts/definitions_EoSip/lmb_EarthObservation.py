from sipMessageBuilder import SipMessageBuilder


class lmb_EarthObservation(SipMessageBuilder):
    
    this = ["lmb:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</lmb:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomenonTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]


