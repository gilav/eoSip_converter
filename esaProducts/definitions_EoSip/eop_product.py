from sipMessageBuilder import SipMessageBuilder


class eop_product(SipMessageBuilder):
    
    this = ["<eop:product>", "</eop:product>"]

    REPRESENTATION = [
        "<eop:ProductInformation>",
        "<eop:fileName>",
        "<ows:ServiceReference xlink:href='@href@'>",
        "<ows:RequestMessage></ows:RequestMessage>",
        "</ows:ServiceReference>",
        "</eop:fileName>",
        "<eop:version>@productVersion@</eop:version>",
        "<eop:size uom='Bytes'>@productSize@</eop:size>",
        "</eop:ProductInformation>"]

