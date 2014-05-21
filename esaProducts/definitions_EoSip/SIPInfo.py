from sipMessageBuilder import SipMessageBuilder


class SIPInfo(SipMessageBuilder):
    
    this = ["<SIPInfo>"]

    REPRESENTATION = ["<SIPCreator>@SIPCreator@</SIPCreator>",
                      "<SIPCreationTime>@generationTime@</SIPCreationTime>"]

    FIELDS = ['SIPCreator', 'SIPCreationTime']

    MANDATORY = ['SIPCreator', 'SIPCreationTime']


