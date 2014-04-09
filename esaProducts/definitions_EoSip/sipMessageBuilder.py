import os,sys,inspect
import logging

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,currentdir)

from sipBuilder import SipBuilder

class SipMessageBuilder(SipBuilder):

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
    # evaluate things like: $$self.getNextCounter()$$
    # in the context of the Metadata object
    #
    def resolveEval_(self, segment, met=None):
        pos=segment.find('$$')
        if pos>=0:
            pos2=pos
            n=0
            result=''
            while pos>=0 and pos2>=0:
                if self.debug!=0:
                    print " @@@@ actual eval segment[%d]:'%s'" % (n, segment)
                pos2=segment.find('$$', pos+2)
                varName=segment[pos+2:pos2]
                if self.debug!=0:
                    print " @@@@ resolve eval[%d]:'%s'" % (n, varName)
                value=met.eval(varName)
                if self.debug!=0:
                    print " @@@@ resolve eval:'%s'->'%s'" % (varName, value)
                result="%s%s%s" % (result, segment[0:pos], value)
                segment=segment[pos2+2:]
                pos=segment.find('$$')
            result="%s%s" % (result, segment)
            if self.debug!=0:
                print " @@@@ resolved eval:'%s'" % result
            return result
        else:
            return segment



    #
    # resolve variable inside @varName@
    #
    def resolveVarname_(self, segment, met=None):
            pos=segment.find('@')
            if self.debug!=0:
                print " @@@@ to be varName resolved:'%s'" % segment
            pos2=pos
            n=0
            result=''
            while pos>=0 and pos2>=0:
                if self.debug!=0:
                    print " @@@@ actual varName segment[%d]:'%s'" % (n, segment)
                pos2=segment.find('@', pos+1)
                varName=segment[pos+1:pos2]
                if self.debug!=0:
                    print " @@@@ resolve varname[%d]:'%s'" % (n, varName)
                value=self.resolveField(varName, met)
                if self.debug!=0:
                    print " @@@@ resolve varname:'%s'->'%s'" % (varName, value)
                result="%s%s%s" % (result, segment[0:pos], value)
                segment=segment[pos2+1:]
                pos=segment.find('@')
            result="%s%s" % (result, segment)
            if self.debug!=0:
                print " @@@@ varName resolved:'%s'" % result
            return result


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
    def _buildMessage(self, this, representation, metadata, currentTreePath):
        deepness=len(currentTreePath.split('/'))-1
        if self.debug!=0:
            print "\n\n==> buildMessage at currentTreePath:"+currentTreePath+"  deepness:%d on this:" % deepness
        n=0
        firstField=None
        lastField=None
        for field in this:
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
        sipMessage=self.addToSipMessageLn(sipMessage, this[0], metadata)
        if self.debug!=0:
            print  " => after this; mess is now:%s" % sipMessage

            
        n=0
        for field in representation:
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
                    #print " @@@@@@@@@hello@@@@@@@@@@@@@@ newCurrentTreePath :%s" % (newCurrentTreePath)
                    
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
        if len(representation) > 0: # need to write closing node
            if len(this) == 1: # only starting node is given
                if  not this[0].strip()[-2:] == '/>':  # and is not also a closing node
                    if self.debug!=0:
                        print "#################%s######" % this[0][-2:]
                        print "################# CREATE CLOSING NODE"
                    sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                    sipMessage=self.addToSipMessage(sipMessage, "</", metadata)
                    sipMessage=self.addToSipMessageLn(sipMessage,this[0][1:], metadata)
                    done = 1
                else:
                    if self.debug!=0:
                        print "#################%s######" % this[0][-2:]
                        print "################# ALREADY CLOSED NODE"
                
            else: # use given closing node
                sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                sipMessage=self.addToSipMessageLn(sipMessage, self.this[1], metadata)
                done = 1
            
        elif done==0:
            if len(this) == 1:
                if this[0].strip()[-2:]=='/>':
                    if self.debug!=0:
                        print "#################%s######" % this[0][-2:]
                        print "################# CREATE CLOSING NODE"
                    # the only node given is also a closing node
                    pass
                else:
                    if self.debug!=0:
                        print "#################%s######" % this[0][-2:]
                        print "################# ALREADY CLOSED NODE"
                    sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                    sipMessage=self.addToSipMessage(sipMessage, "</", metadata)
                    sipMessage=self.addToSipMessageLn(sipMessage, this[0][1:], metadata)
                    done = 1
            else:
                sipMessage="%s%s" %  (sipMessage, self.makeIndent(deepness))
                sipMessage=self.addToSipMessageLn(sipMessage, this[1], metadata)
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
