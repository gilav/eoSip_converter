from sipMessageBuilder import SipMessageBuilder


class rep_rectifiedBrowse(SipMessageBuilder):
    
    this = ["<rep:rectifiedBrowse>", "    </rep:rectifiedBrowse>"]

    REPRESENTATION = ["    <rep:coordList>@BrowseRectCoordList@</rep:coordList>"]
