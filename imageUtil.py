# -*- coding: cp1252 -*-
#
# 
#
#
import sys
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


debug=1
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
        try:
            makeJpegPil(src, dest, resizePercent, w, h, enhance)
        except Exception, e:
            print " can not make jpeg using PIL:"
            if debug!=0:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exc(file=sys.stdout)
            try:
                externalMakeJpeg(src, dest)
            except Exception, e:
                print " Error making jpeg using external call:"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exc(file=sys.stdout)
                #raise e
                pass
    else:
        try:
            externalMakeJpeg(src, dest)
        except Exception, e:
            print " Error making jpeg using external call:"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exc(file=sys.stdout)
            #raise e
            pass
        

#
#
#
def externalMakeJpeg(src=None, dest=None):
    try:
        src=src.replace("//","/")
        dest=dest.replace("//","/")
        if debug!=0:
            print " external resize image:%s into:%s" % (src, dest)
        command="%s %s %s\"" % (externalConverterCommand, src, dest)
        if debug!=0:
            print "command:%s" % command
        retval = subprocess.call(command, shell=True)
        if debug!=0:
            print "  retval:%s" % retval
        if retval!=0:
            raise Exception("Error externalMakeJpeg:")
        if debug!=0:
            print "  jpeg saved as:%s" % dest
    except Exception, e:
        print " externalMakeJpeg error:"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
        raise e
    
#
# NOT USED
#
def externalMakeJpeg__(src=None, dest=None):
    try:
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
    except Exception, e:
        print " externalMakeJpeg error:"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
        raise e


#
#
#
def splitBands(img=None):
    newIm=None
    try:
        r, g, b, a = img.split()
        if debug!=0:
            print "  im splitted"
        newIm = Image.merge("RGB", (r, g, b))
    except:
        r, g, b = img.split()
        if debug!=0:
            print "  im splitted"
        newIm = Image.merge("RGB", (r, g, b))
    return newIm
    
#
#
#
def makeJpegPil(src=None, dest=None, resizePercent=-1, w=-1, h=-1, enhance=None):
    try:
        if debug==0:
            print " internal resize image:%s into:%s; percent:%s" % (src, dest, resizePercent)
        im = Image.open(src)
        if debug==0:
            print "  src image readed:%s" % im.info

        img=None
        if enhance != None:
            converter = ImageEnhance.Contrast(im)
            newIm = converter.enhance(1.5)
            
            #r, g, b, a = img.split()
            #if debug!=0:
            #    print "  im splitted"
            #newIm = Image.merge("RGB", (r, g, b))
            #newIm = splitBands(img)
        else:
            #try:       
            #    r, g, b, a = im.split()
            #    if debug!=0:
            #        print "  im splitted rgba"
            #    newIm = Image.merge("RGB", (r, g, b))
            #except:
            #    r, g, b = im.split()
            #    if debug!=0:
            #        print "  im splitted rgb"
            #    newIm = Image.merge("RGB", (r, g, b))
            newIm = im.copy()
            
        if debug!=0:
            print "  newIm:%s" % newIm

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
    except Exception, e:
        print " Error making jpeg:"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exc(file=sys.stdout)
        #print " !!!!!!!!!!!!!!!!!!!!! FAKE IMAGE GENERATED, to be removed in operation !!!!!!!!!!!!!!!!!!!!!!!!"
        raise e
        #fd=open(dest, "w")
        #fd.write('0')
        #fd.close()

    
if __name__ == '__main__':
    src="C:/Users/glavaux/Shared/LITE/tmp/unzipped/N11-E078_AVN_20090626_PRO_0.tif"
    dest="C:/Users/glavaux/Shared/LITE/TropForest-example/AVNIR/test.jpg"
    ok=makeJpeg(src, dest, 50)
