from sipMessageBuilder import SipMessageBuilder


class rep_browseReport(SipMessageBuilder):
    
    this = ["<rep:browseReport version=\"1.1\" xsi:schemaLocation=\"http://ngeo.eo.esa.int/schema/browseReport IF-ngEO-BrowseReport-1.1.xsd\" xmlns:rep=\"http://ngeo.eo.esa.int/schema/browseReport\" xmlns:opt=\"http://www.opengis.net/opt/2.0\" xmlns:eop=\"http://www.opengis.net/eop/2.0\" xmlns:gml=\"http://www.opengis.net/gml/3.2\" xmlns:om=\"http://www.opengis.net/om/2.0\" xmlns:ows=\"http://www.opengis.net/ows/2.0\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">", "</rep:browseReport>"]

    REPRESENTATION = ["<rep:responsibleOrgName>@responsible@</rep:responsibleOrgName>",
    "<rep:dateTime>@generationTime@</rep:dateTime>",
    "<rep:browseType>@browseType@</rep:browseType>",
    "rep_browse"]
