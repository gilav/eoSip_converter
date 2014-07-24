from sipMessageBuilder import SipMessageBuilder


class SIPInfo(SipMessageBuilder):
    
    this = ["<sip:SIPInfo version=\"2.0\" xmlns:sip=\"http://www.eo.esa.int/SIP/sipInfo/2.0\">","</sip:SIPInfo>"]

    REPRESENTATION = ["<SIPCreator>@SIPCreator@</SIPCreator>",
                      "<SIPCreationTime>@generationTime@</SIPCreationTime>"]



