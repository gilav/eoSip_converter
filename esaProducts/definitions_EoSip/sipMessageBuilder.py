import os,sys,inspect
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,currentdir)

import sipBuilder
from sipBuilder import SipBuilder

class SipMessageBuilder(SipBuilder):

    #
    #
    #
    def buildMessage(self, metadata, currentTreePath):
        return self._buildMessage(metadata, currentTreePath)

    #
    # add to sip message with newline, resolve @xxx@ tags
    #
    def addToSipMessageLn(self, mess, segment, met=None):
        return self.addToSipMessage(mess, "%s\n" % segment, met)
    #
    # add to sip message, resolve @xxx@ tags
    #
    def addToSipMessage(self, mess, segment, met=None):
        if mess!=None:
            pos=segment.find('@')
            if pos<0:
                return "%s%s" % (mess, self.resolveEval(segment, met))
            else:
                mess1 = self.resolveVarname(segment, met)
                return "%s%s" % (mess, self.resolveEval(mess1, met))
        else:
            raise Exception("can not add to None sipMessage")


    #
    # return the 'this' used
    #
    def getThisUsed(self, metadata):
        thisUsed="this_%s" % metadata.getOtherInfo("TYPOLOGY_SUFFIX")

        try:
            res=self.__getattribute__(thisUsed)
            if self.debug != 0:
                print "### getThisUsed: final 'this' for %s:'%s' used:'%s'" % (self, thisUsed, res)
        except:
            res=self.__getattribute__('this')
            print "### getThisUsed: INFO: typology '%s' not available in %s; use 'this':'this'" % (thisUsed, self)

        return res
    

    #
    # return the representation used
    #
    def getRepresentationUsed(self, metadata):
        typologySuffixUsed=metadata.getOtherInfo("TYPOLOGY_SUFFIX")
        res=None
        if typologySuffixUsed==None or typologySuffixUsed=='':
            representation_name=self.TYPOLOGY_DEFAULT_REPRESENTATION
        else:
            representation_name="%s_%s" % (self.TYPOLOGY_DEFAULT_REPRESENTATION, typologySuffixUsed)


        try:
            res=self.__getattribute__(representation_name)
            if self.debug != 0:
                print "### getRepresentationUsed: final representation for %s:'%s' used:'%s'" % (self, representation_name, res)
        except:
            res=self.__getattribute__(self.TYPOLOGY_DEFAULT_REPRESENTATION)
            print "### getRepresentationUsed: WARNING: typology '%s' not available in %s; use:'%s'" % (representation_name, self, self.TYPOLOGY_DEFAULT_REPRESENTATION)

        return res


    #
    #
    def makeIndent(self, n):
        res=''
        for i in range(n):
            res="%s    " % res 
        return res

        
    #
    #
    #
    def _buildMessage(self, metadata, currentTreePath):
        deepness=len(currentTreePath.split('/'))-1
        if self.debug!=0:
            print "\n\n==> buildMessage at currentTreePath:"+currentTreePath+"  deepness:%d on this:" % deepness

        thisToUse=self.getThisUsed(metadata)
        
        n=0
        firstField=None
        lastField=None
        for field in thisToUse:
            if field.strip()[0] != '<':
                raise Exception("field is malformed, wrong start:'%s'" % field)
            elif field.strip()[-1] != '>':
                raise Exception("field is malformed, wrong end:'%s'" % field)

            if n==0:
                firstField=field
            lastField=field
            
            if self.debug!=0:
                print  " field[%d]:%s" % (n, field)
            n=n+1
        if self.debug!=0:
            print  "\n firstField=%s; lastField=%s" % (firstField, lastField)

        sipMessage=self.makeIndent(deepness)
        sipMessage=self.addToSipMessageLn(sipMessage, thisToUse[0], metadata)
        if self.debug!=0:
            print  " => after this; mess is now:%s" % sipMessage

        representationToUse=self.getRepresentationUsed(metadata)
            
        n=0
        for field in representationToUse:
            if self.debug!=0:
                print "  => buildMessage on field[%d]:%s" % (n, field)


            # test if field is in unused map. also test if it is a closing node :</
            used=self.isFieldUsed(field, metadata, currentTreePath)
            if used==1:
                if self.debug!=0:
                    print "    FIELD USED:%s" % field
                if field.strip()[0] == '<':
                    if field[-1] != '>':
                        raise Exception("field is malformed, wrong end:'%s'" % field)
                    sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                    sipMessage=self.addToSipMessageLn(sipMessage, field, metadata)

                else: # other class
                    if self.debug!=0:
                        print "  is in another class"
                    #
                    # windows workarround on filename upercase problem
                    #
                    fieldBis=field
                    pos=field.find('@')
                    if pos >0:
                        fieldBis=field[0:pos]
                        
                    newCurrentTreePath = currentTreePath + "/" + field.replace('_',':')
                    
                    module = __import__(field)
                    class_ = getattr(module, fieldBis)
                    instance = class_()
                    
                    block=instance.buildMessage(metadata, newCurrentTreePath)
                    sipMessage=self.addToSipMessage(sipMessage, block, metadata)
            else:
                if self.debug!=0:
                    print "    FIELD UNUSED:%s" % field
        if self.debug!=0:
            print "   done representation; message=%s" % sipMessage 

        closureNeeded = 0;
        done = 0;
        if len(representationToUse) > 0: # need to write closing node
            if len(thisToUse) == 1: # only starting node is given
                if  not thisToUse[0].strip()[-2:] == '/>':  # and is not also a closing node
                    if self.debug!=0:
                        print "#################%s######" % thisToUse[0][-2:]
                        print "################# CREATE CLOSING NODE"
                    sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                    sipMessage=self.addToSipMessage(sipMessage, "</", metadata)
                    sipMessage=self.addToSipMessageLn(sipMessage,thisToUse[0][1:], metadata)
                    done = 1
                else:
                    if self.debug!=0:
                        print "#################%s######" % thisToUse[0][-2:]
                        print "################# ALREADY CLOSED NODE"
                
            else: # use given closing node
                sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                sipMessage=self.addToSipMessageLn(sipMessage, thisToUse[1], metadata)
                done = 1
            
        elif done==0:
            if len(thisToUse) == 1:
                if thisToUse[0].strip()[-2:]=='/>':
                    if self.debug!=0:
                        print "#################%s######" % thisToUse[0][-2:]
                        print "################# CREATE CLOSING NODE"
                    # the only node given is also a closing node
                    pass
                else:
                    if self.debug!=0:
                        print "#################%s######" % thisToUse[0][-2:]
                        print "################# ALREADY CLOSED NODE"
                    sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                    sipMessage=self.addToSipMessage(sipMessage, "</", metadata)
                    sipMessage=self.addToSipMessageLn(sipMessage, thisToUse[0][1:], metadata)
                    done = 1
            else:
                sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                sipMessage=self.addToSipMessageLn(sipMessage, thisToUse[1], metadata)
                done = 1

        return sipMessage



if __name__ == '__main__':
    print "start"
    logging.basicConfig(level=logging.WARNING)
    log = logging.getLogger('example')
    try:
        p=SipMessageBuilder()
        mess=p.buildMessage()
        print "message:%s" % mess

        fd=open("./sipProductReport.xml", "w")
        fd.write(mess)
        fd.close()
        print "message written in file:%s" % fd

        
    except Exception, err:
        log.exception('Error from throws():')
