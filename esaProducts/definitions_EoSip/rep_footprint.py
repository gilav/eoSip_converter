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


class rep_footprint(SipMessageBuilder):
    
    this = ["<rep:footprint nodeNumber=\"@numberOfNodes@\">","</rep:footprint>"]

    REPRESENTATION = ["<rep:colRowList>@colRowList@<rep:colRowList>",
                    "<rep:coordList>@coordList@</rep:coordList>"]

    FIELDS = ["numberOfNodes", "colRowList", "coordList"]

    MANDATORY = ["numberOfNodes", "colRowList", "coordList"]

    def __init__(self):
        pass

    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(self.this, self.REPRESENTATION, metadata, currentTreePath)


if __name__ == '__main__':
    print "start"
    aaa=A()
    print "%s" % dir(aaa)
    print "stop"
