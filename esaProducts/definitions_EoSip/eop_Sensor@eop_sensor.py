from sipMessageBuilder import SipMessageBuilder


class eop_Sensor(SipMessageBuilder):
    
    this = ["<eop:Sensor>"]

    REPRESENTATION = ["<eop:sensorType>@sensorType@</eop:sensorType>",
              "<eop:operationalMode>@operationalMode@</eop:operationalMode>",
              "<eop:resolution uom=\"@resolutionUomAttr@\">@resolution@</eop:resolution>"]

    OPTIONAL = ["<eop:resolution uom=\"@resolutionUomAttr@\">@resolution@</eop:resolution>"]
