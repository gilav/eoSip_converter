# -*- coding: cp1252 -*-
#
# 
#
#

from geom import vector2D

debug=0



        
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
    print "\n\n\ntotal angle=%s" % totAngle
        
        
        
    #v = Vec2d(3,4)
    #v1=makeVector(0,30)
    #print "length:%s" % get_length(v1)
