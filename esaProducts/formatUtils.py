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
import time
import datetime
import traceback
import math


monthDict={1:'JAN', 2:'FEB', 3:'MAR', 4:'APR', 5:'MAY', 6:'JUN', 7:'JUL', 8:'AUG', 9:'SEP', 10:'OCT', 11:'NOV', 12:'DEC'}
monthDict2={'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10','NOV':'11', 'DEC':'12'}


debug=0

def utmToLatLon(easting, northing, zone, northernHemisphere=True):
    if northernHemisphere=='S' or northernHemisphere=='s':
            northernHemisphere=False;
    elif northernHemisphere=='N' or northernHemisphere=='n':
            northernHemisphere=True;

            
    if not northernHemisphere:
        northing = 10000000 - northing

    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))

    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

    if not northernHemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

    return (latitude, longitude)


        
def dateFromSec(t, pattern="%y-%m-%d %H:%M:%S"):
        d=datetime.datetime.fromtimestamp(t)
        return d.strftime(pattern)


def dateNow(pattern="%y-%m-%d %H:%M:%S"):
        d=datetime.datetime.fromtimestamp(time.time())
        return d.strftime(pattern)


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


#
# change JAN, FEB, etc.. into 2 digits
#
def normaliseDateString(mess=None):
        for monthName in monthDict2.keys():
                pos = mess.find(monthName)
                if pos >=0:
                        mess=mess.replace(monthName, monthDict2[monthName])
        # change space into T
        mess=mess.replace(' ', 'T')

        #
        pos = mess.find('.')
        if pos>=0:
                mess=mess[0:pos+4]+'Z'
        
        return mess


def EEEtoNumber(s=None):
        res=normaliseNumber(s)
        i=float(res)
        if debug!=0:
                print " ### EEEtoNumber res:'%s'\n" % i
        return "%s" % i
        

#
# change number text:
# - suppress leading and tailing space
# - set length
#
def normaliseNumber(s=None, max=-1, pad=' ', truncate=None):
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

        if len(res) > max:
                # suppress space on right side, troncate if allowed
                while len(res)>max and truncate!=None:
                        res=res[0:-1]

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
        a="Ikonos"
        print "a=='%s' normaliseNumber(a)==>'%s'" % (a, normaliseNumber(a, 2, None, 1))

        
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

        print "Utm(712605, 10000, 21, True) ==> lat:0.090422 Lon:-55.089726567181266 ? :: %s %s" % utmToLatLon(712605, 10000, 21, True)

        print "dateNow:%s" % dateNow()
            
    except Exception, e:
        print " Error"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
