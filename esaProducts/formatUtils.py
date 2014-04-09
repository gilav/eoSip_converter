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
                
def normaliseNumber(s=None, max=-1, pad=' '):
        if debug==1:
            print "normaliseNumber:%s"% s
        if s==None:
            s="#"
            pad='#'
        if len(s) > max:
            return s[0:max]
        while len(s)<max:
            s="%s%s" % (s, pad)
        return s
