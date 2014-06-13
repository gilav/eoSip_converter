from sipMessageBuilder import SipMessageBuilder


class rep_footprint(SipMessageBuilder):
    
    this = ["<rep:footprint nodeNumber=\"@numberOfNodes@\">","</rep:footprint>"]

    REPRESENTATION = ["<rep:colRowList>@colRowList@</rep:colRowList>",
                    "<rep:coordList>@coordList@</rep:coordList>"]
