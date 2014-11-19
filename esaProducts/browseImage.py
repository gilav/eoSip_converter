# -*- coding: cp1252 -*-

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from geom import vector2D
import math
import geomHelper
import formatUtils



#
# a browse class that allow to:
# - check if footprint is closed
# - check if is clock wise/counter clock wise
# - reverse it
# 
#
#
class BrowseImage():
    # browse source path
    sourcePath=None
    # footprint is: 'lat long '...
    footprint=None
    origFootprint=None
    # bounding box
    boondingBox=None
    # center
    centerLat=None
    centerLon=None
    origCenterLat=None
    origCenterLon=None
    # colrowlist is: 'x y '...
    colRowList=None
    origColRowList=None
    #
    num_reverseFootprint=0
    num_reverseColRowList=0
    #
    isSSW=None
    #
    isClosed=None
    # cross +-180 longitude
    isCrossing=None
    #
    debug=0
    #
    valid=True



    #
    #
    #
    def __init__(self):
        pass

    #
    # 
    #
    def setSourcePath(self, p):
        self.sourcePath=f

    #
    #
    #
    def getSourcePath(self):
        return self.sourcePath
    
    #
    #
    #
    def setFootprint(self, f):
        self.footprint=f
        self.origFootprint=f
        self.testIsClosed()
        self.testIsCCW()
        
    #
    #
    #
    def setCenter(self, lat, lon):
        self.origCenterLat=lat
        self.origCenterLat=lon
        self.centerLat=lat
        self.centerLon=lon
        
    #
    #
    #
    def getCenter(self):
        return self.centerLat,self.centerLon
    
    #
    #
    def setColRowList(self, cr):
        self.colRowList=cr
        self.origColRowList=cr

    #
    #
    #
    def getFootprint(self):
        return self.footprint

    #
    #
    #
    def getColRowList(self):
        return self.colRowList

    
    #
    #
    #
    def reverse(self):
        self.reverseFootprint()
        self.reverseColRowList()

    #
    #
    #
    def makeThumbnail(self, path, reducePercent, minDim=None):
        return "makeThumbnail: to be implemented"


    #
    #
    #
    def testCrossing(self):
        if self.footprint==None:
            return
        toks=self.footprint.split(" ")
        nPair = 1
        numPair=len(toks)/2
        if self.debug!=0:
                print " numPair=%s" % numPair
        # test distance in longitudes
        oldLon=None
        for item in range(len(toks)/2):
            lon=toks[(item*2)+1]
            if oldLon!=None:
                print "testCrossing %d, lon=%s, oldLon=%s" % (item, lon, oldLon)
                if float(lon)-float(oldLon) > 180 and float(lon)*float(oldLon) <0:
                    self.isCrossing=True
                    print "@#@#@#@#  CROSSING!"
                    return
            oldLon=lon
        self.isCrossing=False

            
    #
    # get the boundingBox
    #
    def calculateBoondingBox(self):
        if self.footprint==None:
            return
        if self.centerLat==None or self.centerLon==None:
            self.calculateCenter()
            
        self.testCrossing()

        toks=self.footprint.split(" ")
        nPair = 1
        numPair=len(toks)/2
        if self.debug!=0:
            print " calculateEnvelope isCrossing=%s" % self.isCrossing

        maxLat=-90
        minLat=90
        minLon=180
        maxLon=-180
        for item in range(len(toks)/2):
            latn = float(toks[item*2])
            longn = float(toks[item*2+1])

            if latn > maxLat:
                maxLat=latn;
            if latn < minLat:
                minLat=latn

            if longn<0 and self.isCrossing==True:
                longn=longn+360
                if longn>maxLon:
                    maxLon=longn
                if longn<minLon:
                    minLon=longn
            else:
                if longn>maxLon:
                    maxLon=longn
                if longn<minLon:
                    minLon=longn

        if maxLon > 180:
            maxLon = maxLon -360
        if self.debug!=0:
            print "############ minLat=%s  maxLat=%s   minLon=%s   maxLon=%s" % (minLat, maxLat, minLon, maxLon)
        # we want 4 points: uper left corner, then ccw
        self.boondingBox = "%s %s %s %s %s %s %s %s" % (maxLat, minLon, minLat, minLon,
                                                        minLat, maxLon, maxLat, maxLon)
        
    #
    # get the footprint envelope: calculate biggest x/y axe arc-distance from coord[n] to center.
    #
    def calculateEnvelope2(self):
        self.testCrossing()
        if self.footprint==None:
            return
        if self.centerLat==None or self.centerLon==None:
            self.calculateCenter()
            
        toks=self.footprint.split(" ")
        nPair = 1
        numPair=len(toks)/2
        if self.debug!=0:
                print " numPair=%s" % numPair
        maxx = 0
        maxy = 0
        fcenterlat=float(self.centerLat)
        fcenterlon=float(self.centerLon)
        for item in range(len(toks)/2):
            latn = toks[item*2]
            longn = toks[item*2+1]
            dy = geomHelper.arcDistanceBetween(fcenterlat, fcenterlon, float(latn), fcenterlon)
            dx = geomHelper.arcDistanceBetween(fcenterlat, fcenterlon, fcenterlat, float(longn))
            if dx > maxx:
                maxx=dx
            if dy>maxy:
                maxy=dy
                
            print "coords %d, lat=%s, lon=%s;   dx=%s; dy=%s    maxx=%s; maxy=%s" % (nPair, latn, longn, dx, dy, maxx, maxy)
            nPair = nPair+1

        print "==> maxx=%s; maxy=%s" % (maxx, maxy)
        maxLon = math.radians(fcenterlon)+maxx
        minLon = math.radians(fcenterlon)-maxx
        maxLat = math.radians(fcenterlat)-maxy
        minLat = math.radians(fcenterlat)+maxy
        self.boondingBox = "%s %s %s %s %s %s %s %s %s %s" % (math.degrees(minLat), math.degrees(minLon),math.degrees(maxLat), math.degrees(minLon),
                                                        math.degrees(maxLat), math.degrees(maxLon),math.degrees(minLat), math.degrees(maxLon),
                                                        math.degrees(minLat), math.degrees(minLon))

        


    #
    # get the footprint center: use the first and middle point to do it
    #
    def calculateCenter(self):
        # get the first and middle footprint coords
        toks=self.footprint.split(" ")
        #print "2eme coord: lat=%s lon=%s" % (toks[(len(toks)/2)-1], toks[(len(toks)/2)] )
        #self.centerLat, self.centerLon = geomHelper.coordinateBetween(float(toks[0]), float(toks[1]), float(toks[(len(toks)/2)-1]), float(toks[(len(toks)/2)]))
        #print "@@@@@@@@@@@@@@@@@@@@@@@calculateCenter 0:%s  %s" % (self.centerLat,self.centerLon)
        #self.centerLat=formatUtils.EEEtoNumber("%s" % self.centerLat)
        #self.centerLon=formatUtils.EEEtoNumber("%s" % self.centerLon)
        #print "@@@@@@@@@@@@@@@@@@@@@@@calculateCenter 1:%s  %s" % (self.centerLat,self.centerLon)

        # new:
        if len(toks)==10:
            alat, alon = geomHelper.getIntermediatePoint(float(toks[0]), float(toks[1]), float(toks[(len(toks)/2)-1]), float(toks[(len(toks)/2)]), 0.5)
            #print "@@@@@@@@@@@@@@@@@@@@@@@getIntermediatePoint 0:%s  %s" % (alat, alon)

            alat1, alon1 = geomHelper.getIntermediatePoint(float(toks[2]), float(toks[3]), float(toks[(len(toks)/2)+1]), float(toks[(len(toks)/2)+2]), 0.5)
            #print "@@@@@@@@@@@@@@@@@@@@@@@getIntermediatePoint 1:%s  %s" % (alat1, alon1)

            self.centerLat, self.centerLon = geomHelper.getIntermediatePoint(alat, alon, alat1, alon1, 0.5)
            #print "@@@@@@@@@@@@@@@@@@@@@@@getIntermediatePoint 2:%s  %s" % (self.centerLat, self.centerLon)
            self.centerLat = formatUtils.EEEtoNumber("%s" % self.centerLat)
            self.centerLon = formatUtils.EEEtoNumber("%s" % self.centerLon)
        else:
            raise Exception("footprint has not 10 tokens but %d:%s" % (len(toks), self.footprint))
            
        return self.centerLat, self.centerLon
    
    #
    #
    #
    def reverseFootprint(self):
        if self.footprint==None:
            return
        else:
            toks=self.footprint.split(" ")
            ccw=""
            nPair=1
            numPair=len(toks)/2
            if self.debug!=0:
                    print " numPair=%s" % numPair
            for item in range(len(toks)/2):
                    if self.debug!=0:
                            print " pair[%d]:%d:" % (nPair-1, (numPair-nPair)*2)
                    if len(ccw)>0:
                            ccw="%s " % ccw
                    ccw="%s%s %s" % (ccw, toks[(numPair-nPair)*2], toks[(numPair-nPair)*2+1])
                    nPair=nPair+1
            self.footprint=ccw;
            if self.colRowList!=None: # if there is no colRowList, we don't care about being out of sync
                self.num_reverseFootprint=self.num_reverseFootprint+1

            self.testIsCCW()
            return ccw

    #
    #
    #
    def reverseSomeFootprint(self, aFootprint):
        toks=aFootprint.split(" ")
        ccw=""
        nPair=1
        numPair=len(toks)/2
        if self.debug!=0:
                print " numPair=%s" % numPair
        for item in range(len(toks)/2):
                if self.debug!=0:
                        print " pair[%d]:%d:" % (nPair-1, (numPair-nPair)*2)
                if len(ccw)>0:
                        ccw="%s " % ccw
                ccw="%s%s %s" % (ccw, toks[(numPair-nPair)*2], toks[(numPair-nPair)*2+1])
                nPair=nPair+1
        return ccw
        

    #
    #
    #
    def reverseColRowList(self):
        if self.colRowList==None:
            return
        else:
            toks=self.colRowList.split(" ")
            ccw=""
            nPair=1
            numPair=len(toks)/2
            if self.debug!=0:
                    print " numPair=%s" % numPair
            for item in range(len(toks)/2):
                    if self.debug!=0:
                            print " pair[%d]:%d:" % (nPair-1, (numPair-nPair)*2)
                    if len(ccw)>0:
                            ccw="%s " % ccw
                    ccw="%s%s %s" % (ccw, toks[(numPair-nPair)*2], toks[(numPair-nPair)*2+1])
                    nPair=nPair+1
            self.colRowList=ccw;
            self.num_reverseColRowList=self.num_reverseColRowList+1
            return ccw

        
    #
    #
    #
    def testIsClosed(self):
        isClosed=True
        toks=self.footprint.split(' ')
        n=len(toks)
        if n >=4 :
            if toks[0]==toks[n-2] and toks[1]==toks[n-1]:
                self.isClosed=True
            else:
                self.isClosed=False
                
        else:
            raise Exception("footprint has to few pairs:%s" % n)
            

        
    #
    #
    #
    def testIsCCW(self):
        toks=self.footprint.split(' ')
        f=[]
        totAngle=0
        for item in toks:
            f.append(float(item))
        for i in range((len(f)/2)-1):
            n=i*2
            #print "\n\nn:%s  len(f):%d" % (n, len(f))
            y1=f[n]
            x1=f[n+1]
            nn = n+2
            if nn>=len(f):  # we come back to the first point, so use the next one to build the second angle?? normally should never be the case because it's the next test the good one
                if self.debug!=0:
                    print "0 nn=%s>%s so set to:%s" % (nn, len(f), nn-len(f))
                nn=nn-len(f)+2
            y2=f[nn]
            x2=f[nn+1]
            nn = nn+2
            if nn>=len(f): # this should be the good test: we come back to the first point, so use the next one to build the second angle
                if self.debug!=0:
                    print "1 nn=%s>%s so set to:%s" % (nn, len(f), nn-len(f)+2)
                nn=nn-len(f)+2
            y3=f[nn]
            x3=f[nn+1]
            if self.debug!=0:
                print "do point[%s]:%s %s vs %s %s vs %s %s " % (n, x1, y1, x2, y2, x3, y3)
            v1 = vector2D.Vec2d(x2-x1, y2-y1)
            v2 = vector2D.Vec2d(x3-x2, y3-y2)
            #print "\nv1=%s" % v1
            #print "v2=%s" % v2
            angle=v2.get_angle_between(v1)
            if self.debug!=0:
                print ">>>>>>>>>>>angle:%f" % v2.get_angle_between(v1)
            totAngle=totAngle+angle
        if self.debug!=0:
            print "total angle=%s" % totAngle
        if totAngle<0:
            self.isCCW=True
        else:
            self.isCCW=False

    def getIsCCW(self):
        return self.isCCW
    def getIsClosed(self):
        return self.isClosed
        
    def info(self):
        info="browseImage\n"
        info="%s source file path=%s\n" % (info, self.sourcePath)
        info="%s original footprint=%s\n" % (info, self.origFootprint)
        infp="%s original colRowList=%s\n" % (info, self.origColRowList)
        info="%s footprint=%s\n" % (info, self.footprint)
        info="%s colRowList=%s\n" % (info, self.colRowList)
        info="%s center: lat=%s; lon=%s\n" % (info, self.centerLat, self.centerLon)
        info="%s is CCW=%s\n" % (info, self.isCCW)
        info="%s is closed=%s\n" % (info, self.isClosed)
        info="%s boondingBox=%s\n" % (info, self.boondingBox)
        if self.num_reverseColRowList != self.num_reverseFootprint:
            info="%s ERROR: number of reverse footprint != reverse colRowList: %s vs %s\n" % (info, self.num_reverseColRowList, self.num_reverseFootprint)
            self.valid=False
        return info


if __name__ == '__main__':
    browse = BrowseImage()
    # razvan 27
    browse.setFootprint('54.655415 -7.145371 53.940960 -7.356686 53.818336 -6.196528 54.532104 -5.964681 54.655415 -7.145371')
    # bf:
    #browse.setFootprint('44.8291 33.1096 44.1762 32.9438 44.0111 34.1619 44.6621 34.3406 44.8291 33.1096')
    # c4:
    #browse.setFootprint('66.412445 -20.979864 65.727463 -21.312971 65.586067 -19.664280 66.268730 -19.287031 66.412445 -20.979864')
    browse.calculateCenter()
    print browse.info()
    browse.reverse()
    print "\nreversed:"
    print browse.info()
    print "\n\n\n\n"
    
    fd=open("boundingBox_try.txt", "w")
    fd.write(browse.info())
    fd.close()
    
    sys.exit(0)
    # razvan BI
    #browse.setFootprint('50.875046 -1.722543 51.310780 -0.413662 50.546196 0.213645 50.116253 -1.076558 50.875046 -1.722543')
    # f130:
    #browse.setFootprint('51.107277 -3.388437 51.544346 -2.074867 50.715931 -1.393089 50.284798 -2.687346 51.107277 -3.388437')
    # d79f:
    #browse.setFootprint('66.412445 -20.979864 65.727463 -21.312971 65.586067 -19.664280 66.268730 -19.287031 66.412445 -20.979864')
    browse.setFootprint("0.43 112.969 -0.421 112.969 -0.421 113.443 0.43 113.443 0.43 112.969")
    browse.calculateCenter()
    browse.calculateBoondingBox()
    print browse.info()
    fd=open("boundingBox_try.txt", "w")
    fd.write(browse.info())
    fd.close()
    browse.reverse()
    print "\nreversed:"
    print browse.info()
