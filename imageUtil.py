# -*- coding: cp1252 -*-
#
# 
#
#
import subprocess
import traceback
from subprocess import call,Popen, PIPE

PilReady=0
try:
    from PIL import Image
    from PIL import ImageEnhance
    PilReady=1
except:
    pass


debug=0
externalConverterCommand="/bin/sh -c \"/usr/bin/gm convert -verbose -scale 25%"


import struct
import imghdr

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    fhandle = open(fname, 'rb')
    head = fhandle.read(24)
    if len(head) != 24:
        return
    if imghdr.what(fname) == 'png':
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
            return
        width, height = struct.unpack('>ii', head[16:24])
    elif imghdr.what(fname) == 'gif':
        width, height = struct.unpack('<HH', head[6:10])
    elif imghdr.what(fname) == 'jpeg':
        try:
            fhandle.seek(0) # Read 0xff next
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf:
                fhandle.seek(size, 1)
                byte = fhandle.read(1)
                while ord(byte) == 0xff:
                    byte = fhandle.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', fhandle.read(2))[0] - 2
            # We are at a SOFn block
            fhandle.seek(1, 1)  # Skip `precision' byte.
            height, width = struct.unpack('>HH', fhandle.read(4))
        except Exception: #IGNORE:W0703
            return
    else:
        return
    return width, height


#
#
#
def makeJpeg(src=None, dest=None, resizePercent=-1, w=-1, h=-1, enhance=None):
    if PilReady==1:
        makeJpegPil(src, dest, resizePercent, w, h, enhance)
    else:
        externalMakeJpeg2(src, dest)


#
#
#
def externalMakeJpeg2(src=None, dest=None):
    src=src.replace("//","/")
    dest=dest.replace("//","/")
    if debug!=0:
        print " external resize image:%s into:%s" % (src, dest)
    command="%s %s %s\"" % (externalConverterCommand, src, dest)
    print "command:%s" % command
    retval = subprocess.call(command, shell=True)
    print "  retval:%s" % retval
    if retval!=0:
        raise Exception("Error externalMakeJpeg:")
    if debug!=0:
        print "  jpeg saved as:%s" % dest
        
#
#
#
def externalMakeJpeg(src=None, dest=None):
    src=src.replace("//","/")
    dest=dest.replace("//","/")
    if debug!=0:
        print " external resize image:%s into:%s" % (src, dest)
    command="%s %s %s" % (externalConverterCommand, src, dest)
    print "command:%s" % command
    toks=externalConverterCommand.split(" ")
    p = Popen(toks, shell=True, stdout=PIPE, stderr=PIPE)
    out,err=p.communicate()
    retval = p.returncode
    print "  retval:%s" % retval
    if retval!=0:
        raise Exception("Error externalMakeJpeg:%s\n%s" % (out.rstrip(),err.rstrip()))
    if debug!=0:
        print "  jpeg saved as:%s" % dest

#
#
#
def makeJpegPil(src=None, dest=None, resizePercent=-1, w=-1, h=-1, enhance=None):
    try:
        if debug!=0:
            print " internal resize image:%s into:%s; percent:%s" % (src, dest, resizePercent)
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
            print "  jpeg saved as:%s" % dest
    except:
        print " !!!!!!!!!!!!!!!!!!!!! FAKE IMAGE GENERATED, to be removed in operation !!!!!!!!!!!!!!!!!!!!!!!!"
        fd=open(dest, "w")
        fd.write('0')
        fd.close()

    
if __name__ == '__main__':
    src="C:/Users/glavaux/Shared/LITE/TropForest-example/AVNIR/N00-E113_AVN_20090517_PRO_0.tif"
    dest="C:/Users/glavaux/Shared/LITE/TropForest-example/AVNIR/test.jpg"
    ok=makeJpeg(src, dest, 50)
