from sipMessageBuilder import SipMessageBuilder


class alt_EarthObservation(SipMessageBuilder):
    
    this = ["<alt:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\" xmlns:gml=\"http://www.opengis.net/gml/3.2\" xmlns:alt=\"http://www.opengis.net/alt/2.1\" xmlns:eop=\"http://www.opengis.net/eop/2.1\" xmlns:om=\"http://www.opengis.net/om/2.0\" xmlns:ows=\"http://www.opengis.net/ows/2.0\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">", "</alt:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomenonTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]


