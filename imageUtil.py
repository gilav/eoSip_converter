# -*- coding: cp1252 -*-
#
# 
#
#

from PIL import Image
from PIL import ImageEnhance


debug=0

#
def makeJpeg(src=None, dest=None, resizePercent=-1, w=-1, h=-1, enhance=None):
    if debug!=0:
        print " resize file:%s into:%s; percent:%s" % (src, dest, resizePercent)
    im = Image.open(src)
    if debug!=0:
        print "  src image readed:%s" % im.info

    if enhance != None:
        converter = ImageEnhance.Contrast(im)
        img = converter.enhance(1.5)
        r, g, b, a = img.split()
        if debug!=0:
            print "  im splitted"
        newIm = Image.merge("RGB", (r, g, b))
    else:
        r, g, b, a = im.split()
        if debug!=0:
            print "  im splitted"
        newIm = Image.merge("RGB", (r, g, b))
    if debug!=0:
        print "  newIm merged"

    width, height = im.size
    newSize=None
    if resizePercent!=-1:
        nw=width*resizePercent/100
        nh=height*resizePercent/100
        newSize=[nw,nh]
    elif w>0 and h>0:
        newSize=[w,h]

    if newSize!=None:   
        im=newIm.resize(newSize, Image.BILINEAR )
        if debug!=0:
            print "  newIm resized"
        im.save(dest, "JPEG")
    else:
        newIm.save(dest, "JPEG")
    if debug!=0:
        print "  saved as:%s" % dest


    
if __name__ == '__main__':
    src="C:/Users/glavaux/Shared/LITE/TropForest-example/AVNIR/N00-E113_AVN_20090517_PRO_0.tif"
    dest="C:/Users/glavaux/Shared/LITE/TropForest-example/AVNIR/test.jpg"
    ok=makeJpeg(src, dest, 50)
