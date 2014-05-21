from sipMessageBuilder import SipMessageBuilder


class sar_EarthObservation(SipMessageBuilder):
    
    this = ["<sar:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</sar:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomenonTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]


