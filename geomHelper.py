# -*- coding: cp1252 -*-
#
# 
#
#

from geom import vector2D
from math import radians, cos, sin, asin, sqrt, atan2, degrees

debug=0

#
#
#
def coordinateBetween(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    bx = cos(lat2) * cos(lon2 - lon1)
    by = cos(lat2) * sin(lon2 - lon1)
    lat3 = atan2(sin(lat1) + sin(lat2), \
           sqrt((cos(lat1) + bx) * (cos(lat1) \
           + bx) + by**2))
    lon3 = lon1 + atan2(by, cos(lat1) + bx)

    return degrees(lat3), degrees(lon3)

#
# Calculate the great circle distance between two points 
# on the earth (specified in decimal degrees)
# returns the distance in meters
#
def metersDistanceBetween(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    print "angle=%s" % c

    # if we want the distance in meter
    # 6378137f meters is the radius of the Earth
    meters = 6378137 * c
    return meters

#
# Calculate the great circle distance between two points 
# on the earth (specified in decimal degrees)
# returns the arc distance in radian
#
def arcDistanceBetween(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    print "angle=%s" % c

    # if we want the distance in meter
    # 6378137f meters is the radius of the Earth
    #meters = 6378137f * c
    return c


        
if __name__ == '__main__':
    # CW:
    #poly='43.505158383 -9.7328153269 43.400659479 -8.9829417472 42.876066318 -9.1602073246 42.979779308 -9.903779609 43.505158383 -9.7328153269'
    #poly='43.5 -9.73 43.4 -8.98 42.88 -9.16 42.98 -9.9 43.5 -9.73'
    # CCW
    poly='0.43 112.969 -0.421 112.969 -0.421 113.443 0.43 113.443 0.43 112.969'
 
    
    toks=poly.split(' ')
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
            print "0 nn=%s>%s so set to:%s" % (nn, len(f), nn-len(f))
            nn=nn-len(f)+2
        y2=f[nn]
        x2=f[nn+1]
        nn = nn+2
        if nn>=len(f): # this should be the good test: we come back to the first point, so use the next one to build the second angle
            print "1 nn=%s>%s so set to:%s" % (nn, len(f), nn-len(f)+2)
            nn=nn-len(f)+2
        y3=f[nn]
        x3=f[nn+1]
        print "do point[%s]:%s %s vs %s %s vs %s %s " % (n, x1, y1, x2, y2, x3, y3)
        v1 = vector2D.Vec2d(x2-x1, y2-y1)
        v2 = vector2D.Vec2d(x3-x2, y3-y2)
        #print "\nv1=%s" % v1
        #print "v2=%s" % v2
        angle=v2.get_angle_between(v1)
        print ">>>>>>>>>>>angle:%f" % v2.get_angle_between(v1)
        totAngle=totAngle+angle
    print "\n\n\ntotal angle=%s\n\n" % totAngle

    print "distance:%s" % metersDistanceBetween(0.43,112.969,-0.421,142.969)
    print "middle:lat=%s; lon=%s" % coordinateBetween(0.43,112.969,-40.421,142.969)
        
        
        
    #v = Vec2d(3,4)
    #v1=makeVector(0,30)
    #print "length:%s" % get_length(v1)
