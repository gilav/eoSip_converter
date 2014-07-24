# -*- coding: cp1252 -*-

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from geom import vector2D
import geomHelper



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
    def calculateCenter(self):
        # get the first and middle footprint coords
        toks=self.footprint.split(" ")
        #print "2eme coord: lat=%s lon=%s" % (toks[(len(toks)/2)-1], toks[(len(toks)/2)] )
        self.centerLat, self.centerLon = geomHelper.coordinateBetween(float(toks[0]), float(toks[1]), float(toks[(len(toks)/2)-1]), float(toks[(len(toks)/2)]))
        #print "@@@@@@@@@@@@@@@@@@@@@@@calculateCenter:%s  %s" % (self.centerLat,self.centerLon)
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
        if self.num_reverseColRowList != self.num_reverseFootprint:
            info="%s ERROR: number of reverse footprint != reverse colRowList: %s vs %s\n" % (info, self.num_reverseColRowList, self.num_reverseFootprint)
            self.valid=False
        return info


if __name__ == '__main__':
    browse = BrowseImage()
    # razvan MD
    #browse.setFootprint('50.536655 0.184164 51.295147 -0.438592 50.869156 -1.717447 50.116280 -1.076581 50.536655 0.184164')
    # f130:
    #browse.setFootprint('50.706326 -1.422633 51.509552 -2.083871 51.082394 -3.366864 50.284790 -2.687338 50.706326 -1.422633')
    # d79f:
    browse.setFootprint('57.548565 -6.235787 58.214821 -7.003214 57.726082 -8.463278 57.067547 -7.676068 57.548565 -6.235787')
    browse.calculateCenter()
    print browse.info()
    browse.reverse()
    print "\nreversed:"
    print browse.info()
    print "\n\n\n\n"
    # razvan BI
    #browse.setFootprint('50.875046 -1.722543 51.310780 -0.413662 50.546196 0.213645 50.116253 -1.076558 50.875046 -1.722543')
    # f130:
    #browse.setFootprint('51.107277 -3.388437 51.544346 -2.074867 50.715931 -1.393089 50.284798 -2.687346 51.107277 -3.388437')
    # d79f:
    browse.setFootprint('57.555702 -6.213644 57.067524 -7.676043 57.731705 -8.470135 58.227787 -6.987471 57.555702 -6.213644')
    print browse.info()
    browse.reverse()
    print "\nreversed:"
    print browse.info()
