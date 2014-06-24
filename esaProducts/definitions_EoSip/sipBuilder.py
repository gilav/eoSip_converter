#
#
# methods used to build the eoSip xml message
# used by sipMessageBuilder class
#
# Contains also the matadata_name to xml node mapping
#
from abc import ABCMeta, abstractmethod
import sys,os,inspect
import traceback

# to be able to import metadata
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parentdir = os.path.dirname(currentdir)
#print "SYS_PATH:%s" % sys.path
#sys.path.insert(0,parentdir)
import metadata, browse_metadata


VALUE_OPTIONAL="OPTIONAL"
VALUE_CONDITIONS="CONDITIONS"
VALUE_UNKNOWN="UNKNOWN"
VALUE_NONE="None"
VALUE_NOT_PRESENT="NOT-PRESENT"

# default xml node mapping
EOSIP_METADATA_MAPPING={'responsible':metadata.METADATA_RESPONSIBLE,
                        'SIPCreator':metadata.METADATA_CREATOR,
                        'reportType':metadata.METADATA_REPORT_TYPE,
                        'generationTime':metadata.METADATA_GENERATION_TIME,
                        'gmlId':metadata.METADATA_PRODUCTNAME,
                        'identifier':metadata.METADATA_PRODUCTNAME,
                        'parentIdentifier':metadata.METADATA_PRODUCTNAME,
                        'productType':metadata.METADATA_TYPECODE,
                        'beginPositionDate':metadata.METADATA_START_DATE,
                        'beginPositionTime':metadata.METADATA_START_TIME,
                        'endPositionDate':metadata.METADATA_STOP_DATE,
                        'endPositionTime':metadata.METADATA_STOP_TIME,
                        'platformShortName':metadata.METADATA_PLATFORM,
                        'platformSerialIdentifier':metadata.METADATA_PLATFORM_ID,
                        'instrumentShortName':metadata.METADATA_INSTRUMENT,
                        'instrumentDescription':metadata.METADATA_INSTRUMENT_DESCRIPTION,
                        'sensorType':metadata.METADATA_SENSOR_TYPE,
                        'operationalMode':metadata.METADATA_SENSOR_OPERATIONAL_MODE,
                        'orbitNumber':metadata.METADATA_ORBIT,
                        'orbitDirection':metadata.METADATA_ORBIT_DIRECTION,
                        'wrsLongitudeGrid':metadata.METADATA_WRS_LONGITUDE_GRID_NORMALISED,
                        'wrsLatitudeGrid':metadata.METADATA_WRS_LATITUDE_GRID_NORMALISED,
                        'illuminationAzimuthAngle':metadata.METADATA_SUN_AZIMUTH,
                        'instrumentElevationAngle':metadata.METADATA_INSTRUMENT_ZENITH_ANGLE,
                        'illuminationElevationAngle':metadata.METADATA_SUN_ELEVATION,
                        'incidenceAngle':metadata.METADATA_INSTRUMENT_INCIDENCE_ANGLE,
                        'instrumentZenithAngle':metadata.METADATA_INSTRUMENT_ZENITH_ANGLE,
                        'instrumentElevationAngle':metadata.METADATA_INSTRUMENT_ELEVATION_ANGLE,
                        'productSize':metadata.METADATA_PRODUCT_SIZE,
                        'referenceSystemIdentifier':metadata.METADATA_REFERENCE_SYSTEM_IDENTIFIER,
                        'href':metadata.METADATA_PACKAGENAME,
                        'timePosition':metadata.METADATA_PROCESSING_TIME,
                        'cloudCoverPercentage':metadata.METADATA_CLOUD_COVERAGE,
                        'status':metadata.METADATA_STATUS,
                        'acquisitionType':metadata.METADATA_ACQUISITION_TYPE,
                        'coordList':metadata.METADATA_FOOTPRINT,
                        'numberOfNodes':'BROWSE_METADATA_FOOTPRINT_NUMBER_NODES',
                        'browseType':browse_metadata.BROWSE_METADATA_BROWSE_TYPE,
                        'browsesType':metadata.METADATA_BROWSES_TYPE,
                        'codeSpace_referenceSystemIdentifier':metadata.METADATA_CODESPACE_REFERENCE_SYSTEM,
                        'browseImageType':browse_metadata.BROWSE_METADATA_IMAGE_TYPE,
                        'browseIdentifier':browse_metadata.BROWSE_METADATA_FILENAME,
                        'browseFileName':browse_metadata.BROWSE_METADATA_NAME,
                        'BrowseRectCoordList':browse_metadata.BROWSE_METADATA_RECT_COORDLIST,
                        'colRowList':metadata.METADATA_FOOTPRINT_IMAGE_ROWCOL,
                        'processingDate':metadata.METADATA_PROCESSING_TIME,
                        'processingCenter':metadata.METADATA_PROCESSING_CENTER,
                        'processorName':metadata.METADATA_SOFTWARE_NAME,
                        'processorVersion':metadata.METADATA_SOFTWARE_VERSION,
                        'cycleNumber':metadata.METADATA_CYCLE,
                        'relativePassNumber':metadata.METADATA_RELATIVE_ORBIT,
                        'snowCoverPercentage':metadata.METADATA_SNOW_COVERAGE,
                        'sceneCenter':metadata.METADATA_SCENE_CENTER
                        }


TYPOLOGY_EOP=0
TYPOLOGY_SAR=1
TYPOLOGY_OPT=2
TYPOLOGY_LMB=3
TYPOLOGY_ALT=4
TYPOLOGY_LIST=[TYPOLOGY_EOP, TYPOLOGY_SAR, TYPOLOGY_OPT, TYPOLOGY_LMB, TYPOLOGY_ALT]
TYPOLOGY_REPRESENTATION_SUFFIX=['EOP', 'SAR', 'OPT', 'LMB', 'ALT']
TYPOLOGY_DEFAULT_REPRESENTATION='REPRESENTATION'

class SipBuilder:
    __metaclass__=ABCMeta

    debug=0
    # the matadata to xml node mapping in use
    USED_METADATA_MAPPING=EOSIP_METADATA_MAPPING


    def __init__(self):
        pass

    @abstractmethod
    def buildMessage(self, representation, metadata, currentTreePath):
        raise Exception("abstractmethod")


    #
    # condition value is like:"FILLED__acquisitionStation"
    #
    def checkConditions(self, metadata=None, condition=None):
        try:
            result=False
            pos = condition.find('__')
            operator=condition[0:pos]
            metaName=condition[pos+2:]
            print "################################## checkConditions: operator:'%s'  varname='%s'" % (operator, metaName)
            if metadata.dict.has_key(metaName):
                resolved=metadata.getMetadataValue(metaName)
                if operator=="FILLED":
                    if resolved!=None and resolved!=VALUE_NONE and resolved!=VALUE_UNKNOWN and resolved!=VALUE_NOT_PRESENT:
                        result=true
                else:
                    raise Exception("unknown condition operator:'%s'" % operator)
            else:
                print "################################## checkConditions: metaName not in metadata:'%s'" % metaName
            print "################################## checkConditions: returns:%s" % result
            return result
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print "################################## checkConditions: ERROR:%s  %s\n%s\n" %  (exc_type, exc_obj, traceback.format_exc())
            raise e
            

    #
    # return a field name, from:
    # - field xml representation like: "<gml:orbitNumber>@orbitNumber@</gml:orbitNumber>" ==> gml:orbitNumber
    # - field xml representation like: "<opt:cloudCoverPercentage uom='%'>@cloudCoverPercentage@</opt:cloudCoverPercentage>" ==> opt:cloudCoverPercentage
    # - class name like: "eop_earthObservation" ==> eop:earthObservation
    #
    def getFieldName(self, rep=None):
        if rep.strip()[0]=='<':
            pos = rep.find('>')
            if pos<0:
                raise Exception("field is malformed: no end >:%s" % rep)
            rep=rep[1:pos]
            pos = rep.find(" ")
            if pos > 0:
                rep=rep[0:pos]
            return rep
        else:
            pos = rep.find('_')
            if pos<0:
                raise Exception("field is malformed: no _ in class name:%s" % rep)
            return rep.replace('_',':')

    #
    # check if a field is in the xml used map
    # based on field path like: /rep:browseReport/rep_browse/rep:referenceSystemIdentifier=UNUSED
    # 
    #
    def isFieldUsed(self, rep=None, metadata=None, path=None):
        if self.debug!=0:
            print "### isFieldUsed: test rep:'%s' at path:'%s'" % (rep, path)
        if path[0]!='/':
            path="/%s" % (path)
        # is closing node:
        if rep[0:2]=='</':
            if self.debug!=0:
                print "### isFieldUsed: CLOSING NODE: USED"
            return 1
        # normalyse path 
        # replace path blocks like '/eop_Sensor@eop_sensor/...' with eop_Sensor
        # this is because of windows filename case problem, so workarround
        pos = path.find('@')
        pathOk=''
        while pos>0:
            #raise Exception("TEST @ in path")
            pathOk=pathOk+path[0:pos]
            if self.debug!=0:
                print "### isFieldUsed: pathOk:'%s'" % pathOk
            endPos=path.find('/')
            if endPos>0:
                pos = path.find('@', endPos+1)
                if self.debug!=0:
                    print "### isFieldUsed: pathOk remain from pos:'%d'" % pos
            else:
                pos=-1
                if self.debug!=0:
                    print "### isFieldUsed: pathOk end"

        if len(pathOk)==0:
            pathOk=path

        #pathOk=pathOk.replace(":","_")
        if self.debug!=0:
            print "### isFieldUsed: pathOk:'%s'" % pathOk
        name=self.getFieldName(rep)
        metDebug=metadata.debug
        if self.debug!=0:
            print "### isFieldUsed: name:'%s'" % name
            metadata.debug=2
        res=metadata.isFieldUsed("%s/%s" % (pathOk, name))
        metadata.debug=metDebug
        return res


    #
    # resolve a field string, may contains varName or/and eval patterns
    #
    #
    def resolveField(self, name, metadata=None):
        if self.USED_METADATA_MAPPING.has_key(name):
            metaName=self.USED_METADATA_MAPPING[name]
            if self.debug!=0:
                print " resolveField: '%s' in metadata name:%s"% (name, metaName)
            try:
                resolved=metadata.getMetadataValue(metaName)
            except Exception, e:
                print " Error:"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exc(file=sys.stdout)
                resolved='ERROR! %s; %s' % (exc_type, exc_obj)
            return resolved
        else:
            if self.debug==2:
                print "resolveField: metadata dump:\n%s" % metadata.toString()
            return VALUE_UNKNOWN


    #
    # evaluate things like: $$self.getNextCounter()$$
    # in the context of the Metadata object
    #
    def resolveEval(self, segment, met=None):
        pos=segment.find('$$')
        if pos>=0:
            pos2=pos
            n=0
            result=''
            while pos>=0 and pos2>=0:
                if self.debug!=0:
                    print "### resolveEval: actual eval segment[%d]:'%s'" % (n, segment)
                pos2=segment.find('$$', pos+2)
                varName=segment[pos+2:pos2]
                if self.debug!=0:
                    print "### resolveEval: eval[%d]:'%s'" % (n, varName)
                value=met.eval(varName)
                if self.debug!=0:
                    print "### resolveEval: eval:'%s'->'%s'" % (varName, value)
                result="%s%s%s" % (result, segment[0:pos], value)
                segment=segment[pos2+2:]
                pos=segment.find('$$')
            result="%s%s" % (result, segment)
            if self.debug!=0:
                print "### resolveEval: resolved eval:'%s'" % result
            return result
        else:
            return segment


    #
    # resolve variable inside @varName@
    # in the context of the Metadata object
    #
    def resolveVarname(self, segment, met=None):
            pos=segment.find('@')
            if self.debug!=0:
                print "### resolveVarname: to be varName resolved:'%s'" % segment
            pos2=pos
            n=0
            result=''
            while pos>=0 and pos2>=0:
                if self.debug!=0:
                    print "### resolveVarname: actual varName segment[%d]:'%s'" % (n, segment)
                pos2=segment.find('@', pos+1)
                varName=segment[pos+1:pos2]
                if self.debug!=0:
                    print "### resolveVarname: resolve varname[%d]:'%s'" % (n, varName)
                value=self.resolveField(varName, met)
                if self.debug!=0:
                    print "### resolveVarname: resolve varname:'%s'->'%s'" % (varName, value)
                result="%s%s%s" % (result, segment[0:pos], value)
                segment=segment[pos2+1:]
                pos=segment.find('@')
            result="%s%s" % (result, segment)
            if self.debug!=0:
                print "### resolveVarname: varName resolved:'%s'" % result
            return result
