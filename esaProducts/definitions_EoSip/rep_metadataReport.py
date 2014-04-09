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


class rep_metadataReport(SipMessageBuilder):
    
    this = ["<rep:metadataReport version=\"1.2\" xsi:schemaLocation=\"http://ngeo.eo.esa.int/schema/metadataReport IF-ngEO-MetadataReport.xsd\" xmlns:rep=\"http://ngeo.eo.esa.int/schema/metadataReport\" xmlns:opt=\"http://www.opengis.net/opt/2.0\" xmlns:eop=\"http://www.opengis.net/eop/2.0\" xmlns:gml=\"http://www.opengis.net/gml/3.2\" xmlns:om=\"http://www.opengis.net/om/2.0\" xmlns:ows=\"http://www.opengis.net/ows/2.0\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">", "</rep:metadataReport>"]

    REPRESENTATION = ["<rep:responsibleOrgName>@responsible@</rep:responsibleOrgName>",
        "<rep:reportType>@reportType@</rep:reportType>",
        "<rep:dateTime>@generationTime@</rep:dateTime>",
        "eop_EarthObservation"]

    FIELDS = ['responsible', 'reportType', 'generationTime']

    MANDATORY = ['responsible', 'reportType', 'generationTime']

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)



    def test(self):
        meta=Metadata()
        meta.setMetadataPair(meta.METADATA_START_DATE, '20021023')
        mess=self.buildMessage(meta, "rep.metadataReport")
        print "message:%s" % mess
        return mess


if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        c=rep_metadataReport()
        mess=c.test()

        fd=open("./sipProductReport.xml", "w")
        fd.write(mess)
        fd.close()
        print "message written in file:%s" % fd
    except Exception, err:
        log.exception('Error from throws():')
