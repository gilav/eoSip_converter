from sipMessageBuilder import SipMessageBuilder


class rep_browse(SipMessageBuilder):
    
    this = ["<rep:browse>"]

    REPRESENTATION = ["<rep:browseIdentifier>@browseIdentifier@</rep:browseIdentifier>",
                      "<rep:fileName>@browseFileName@</rep:fileName>",
                      "<rep:imageType>@browseImageType@</rep:imageType>",
                      "<rep:referenceSystemIdentifier>@referenceSystemIdentifier@</rep:referenceSystemIdentifier>",
                      "<BROWSE_CHOICE></BROWSE_CHOICE>",
                      "<rep:startTime>@beginPositionDate@T@beginPositionTime@Z</rep:startTime>",
                      "<rep:endTime>@endPositionDate@T@endPositionTime@Z</rep:endTime>"]
