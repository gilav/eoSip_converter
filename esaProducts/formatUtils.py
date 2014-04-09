#!/usr/bin/env python
#
# 
# Lavaux Gilles 2013
#
#
import os
import sys
import xml.dom.minidom
import StringIO
import traceback


debug=0

def normaliseDate(s=None, max=-1, pad='#'):
        if s != None:
            return s.replace('-', '')
        else:
            s=''
            while len(s)<max:
             s="%s%s" % (s, pad)
            return s

def normaliseTime(s=None, max=-1, pad='#'):
        if s != None:
            return s.replace(':', '')
        else:
            s=''
            while len(s)<max:
             s="%s%s" % (s, pad)
            return s


def EEEtoNumber(s=None):
        res=normaliseNumber(s)
        i=float(res)
        if debug!=0:
                print " ### EEEtoNumber res:'%s'\n" % i
        return "%s" % i
        
        
def normaliseNumber(s=None, max=-1, pad=' '):
        if debug!=0:
            print "normaliseNumber:'%s'" % s
        if s==None:
            s="#"
            pad='#'
        s=s.strip()
        
        if debug!=0:
                print " normaliseNumber after strip; s:'%s'" % s
        if max==-1:
                max=len(s)

        res=s
        if len(res) > max:
                # suppress space on left side
                while len(res)>max and res[0]==' ':
                        res=res[1:]

        if debug!=0:
                print " normaliseNumber after max; res:'%s'" % res
        while len(res)<max:
            res="%s%s" % (pad, res)

        if debug!=0:
                print " ### normaliseNumber res:'%s'\n" % res
        return res



def reverseFootprint(footprint):
        toks=footprint.split(" ")
        ccw=""
        nPair=1
        numPair=len(toks)/2
        if debug!=0:
                print " numPair=%s" % numPair
        for item in range(len(toks)/2):
                if debug!=0:
                        print " pair[%d]:%d:" % (nPair-1, (numPair-nPair)*2)
                if len(ccw)>0:
                        ccw="%s " % ccw
                ccw="%s%s %s" % (ccw, toks[(numPair-nPair)*2], toks[(numPair-nPair)*2+1])
                nPair=nPair+1
        return ccw
                
        


if __name__ == '__main__':
    try:
        a="          1"
        print "a=='%s' normaliseNumber(a)==>'%s'" % (a, normaliseNumber(a))
        print "a=='%s' normaliseNumber(a,4)==>'%s'" % (a, normaliseNumber(a,4))
        print "a=='%s' normaliseNumber(a,-1)==>'%s'" % (a, normaliseNumber(a,8))
        a="   +1.2345E02   "
        print "a=='%s' normaliseNumber(a,4)==>'%s'" % (a, normaliseNumber(a,8))
        print "a=='%s' EEEtoNumber(a)==>'%s'" % (a, EEEtoNumber(a))
        a="   -1.2345E02   "
        print "a=='%s' EEEtoNumber(a)==>'%s'" % (a, EEEtoNumber(a))
        cwFootprint="11.505158383 -1.7328153269 22.400659479 -2.9829417472 33.876066318 -3.1602073246 44.979779308 -4.903779609 55.505158383 -5.7328153269"
        ccw=reverseFootprint(cwFootprint)
        print "footprint:%s" % cwFootprint
        print "ccw:%s" % ccw
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
