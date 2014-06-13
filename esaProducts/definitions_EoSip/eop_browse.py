from sipMessageBuilder import SipMessageBuilder


class eop_browse(SipMessageBuilder):
    
    this = ["<eop:browse>", "</eop:browse>"]

    REPRESENTATION = [
                "<eop:BrowseInformation>",
                "<eop:type>@browsesType@</eop:type>",
                "<eop:referenceSystemIdentifier codeSpace=\"@codeSpace_referenceSystemIdentifier@\">@referenceSystemIdentifier@</eop:referenceSystemIdentifier>",
                "<eop:fileName>",
                "<ows:ServiceReference xlink:href='@browseIdentifier@'>",
                "<ows:RequestMessage></ows:RequestMessage>",
                "</ows:ServiceReference>",
                "</eop:fileName>",
                "</eop:BrowseInformation>"]

