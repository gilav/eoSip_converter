import os,sys,inspect
import logging
#

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
try:
    sys.path.index(parentdir)
except:
    sys.path.insert(0,parentdir)

from metadata import Metadata
from definitions_EoSip.sipMessageBuilder import SipMessageBuilder


class rep_browseReport(SipMessageBuilder):
    
    this = ["<rep:browseReport version=\"1.1\" xsi:schemaLocation=\"http://ngeo.eo.esa.int/schema/browseReport IF-ngEO-BrowseReport-1.1.xsd\" xmlns:rep=\"http://ngeo.eo.esa.int/schema/browseReport\" xmlns:opt=\"http://www.opengis.net/opt/2.0\" xmlns:eop=\"http://www.opengis.net/eop/2.0\" xmlns:gml=\"http://www.opengis.net/gml/3.2\" xmlns:om=\"http://www.opengis.net/om/2.0\" xmlns:ows=\"http://www.opengis.net/ows/2.0\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">", "</rep:browseReport>"]

    REPRESENTATION = ["<rep:responsibleOrgName>@responsible@</rep:responsibleOrgName>",
    "<rep:dateTime>@generationTime@</rep:dateTime>",
    "<rep:browseType>@browseType@</rep:browseType>",
    "rep_browse"]

    FIELDS = ['dateTime', 'browseType']

    MANDATORY = ['dateTime', 'browseType']

    def __init__(self):
        pass


    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)


    def test(self):
        meta=Metadata()
        meta.setMetadataPair('dateTime', '20021023')
        meta.setMetadataPair('browseType','jpeg')
        mess=self.buildMessage(meta, "rep.browseReport")
        print "message:%s" % mess
        return mess


if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        c=rep_browseReport()
        mess=c.test()

        fd=open("./sipBrowseReport.xml", "w")
        fd.write(mess)
        fd.close()
        print "message written in file:%s" % fd
    except Exception, err:
        log.exception('Error from throws():')
