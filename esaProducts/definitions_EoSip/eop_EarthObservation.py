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


class eop_EarthObservation(SipMessageBuilder):
    
    this = ["<eop:EarthObservation gml:id=\"@gmlId@_$$getNextCounter()$$\">", "</eop:EarthObservation>"]

    REPRESENTATION = [
        "om_phenomeneTime",
        "om_resultTime",
        "om_procedure",
        "om_observedProperty",
        "om_featureOfInterest",
        "om_result",
        "eop_metaDataProperty"
        ]


    def test(self):
        meta=Metadata()
        meta.setMetadataPair(meta.METADATA_START_DATE, '20021023')
        mess=self.buildMessage(meta, "eop.EarthObservation")
        print "message:%s" % mess
        return mess


if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        c=eop_earthObservation()
        mess=c.test()

        fd=open("./sipProductReport.xml", "w")
        fd.write(mess)
        fd.close()
        print "message written in file:%s" % fd
    except Exception, err:
        log.exception('Error from throws():')
