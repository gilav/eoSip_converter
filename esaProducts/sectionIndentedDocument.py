#!/usr/bin/env python
#
# 
# Lavaux Gilles 2013
#
#
import os
import time
import sys
import re
from os import walk




class SectionDocument:
    
    debug=0
    
    def __init__(self):
        #
        #debug=0
        # section:lineNumber
        self.sectionMap={}
        #
        self.lines=None
        if self.debug!=0:
            print " SectionDocument created"

        
    #
    #
    #
    def loadDocument(self, path=None):
        if self.debug!=0:
            print " loadDocument at path;%s" % path
        fd=open(path,'r')
        self.lines=fd.readlines()
        fd.close()


    #
    # section can end with * pattern:
    # 'sectionName blablabla...' or 'sectionName*'
    #
    def getSectionLine(self, section):
        if self.debug!=0:
            print " getSectionLine for section:'%s'" % (section)
        posLine=-1
        if not section[-1]=='*':
            if self.sectionMap.has_key(section):
                posLine=self.sectionMap[section]
                if self.debug!=0:
                    print " getSectionLine for section:%s  already known at line:%d" % (section, posLine)
            else:
                n=0
                for line in self.lines:
                    if line.strip()==section:
                        if self.debug!=0:
                            print " getSectionLine section :%s found at line:%d" % (section, n)
                        self.sectionMap[key]=n
                        posLine=n
                        break
                    n=n+1
            if posLine==-1:
                raise Exception("section not found:'%s'" % section)
        else:
            n=0
            for line in self.lines:
                if line[0:len(section[0:-1])]==section[0:-1]:
                    if self.debug!=0:
                        print " getSectionLine section :%s found at line:%d" % (section, n)
                    posLine=n
                    break
                n=n+1
        if posLine==-1:
            raise Exception("section '%s' not found" % section)
        return posLine

    #
    #
    #
    def getLineValue(self, posLine, name=None):
        pos = self.lines[posLine].find(':')
        if pos>0:
            name=self.lines[posLine][0:pos].strip()
            if self.debug!=0:
                print "  getValue: name:'%s'" % name
            value=self.lines[posLine][pos+1:]
            if self.debug!=0:
                print "  getValue 00: found:'%s'" % value
            value=value.replace('\n','')
            value=value.replace('\r','')
            if self.debug!=0:
                print "  getValue 11: found:'%s'" % value
            return value
        else:
            raise Exception("no ':' in line:%s" % self.lines[posLine])
        
    #
    #
    #
    def getValue(self, section, key, lineNum=0):
        if self.debug!=0:
            print " getValue for section:'%s' key:'%s'" % (section, key)
        posLine=-1
        if self.sectionMap.has_key(section):
            posLine=self.sectionMap[section]
            if self.debug!=0:
                print " getValue for section:%s  already known at line:%d" % (section, posLine)
        else:
            n=0
            for line in self.lines:
                if line.strip()==section:
                    if self.debug!=0:
                        print " getValue for section:%s found at line:%d" % (section, n)
                    self.sectionMap[key]=n
                    posLine=n
                    break
                n=n+1
        endSection=0
        if posLine==-1:
            raise Exception("section not found:'%s'" % section)
        posLine=posLine+1
        value=None
        while not endSection==1 and posLine<len(self.lines):
            if self.debug!=0:
                print "  getValue: test line[%d]:%s" % (posLine, self.lines[posLine])
            if not self.lines[posLine][0]==' ':
                endSection=1
                if self.debug!=0:
                    print "  getValue: end section"
            else:
                pos = self.lines[posLine].find(':')
                if pos>0:
                    name=self.lines[posLine][0:pos].strip()
                    if self.debug!=0:
                        print "  getValue: name:'%s'" % name
                    if key==name:
                        value=self.lines[posLine][pos+1:]
                        if self.debug!=0:
                            print "  getValue 0: found:'%s'" % value
                        value=value.replace('\n','')
                        value=value.replace('\r','')
                        if self.debug!=0:
                            print "  getValue 1: found:'%s'" % value
                        break
            posLine=posLine+1
            if value==None:
                raise Exception("Key '%s' not found" % key)
            return value
            
            



def main():
    """Main funcion"""

    sectionDoc=SectionDocument()
    if len(sys.argv) > 1:
        print "use SectionDocument on path:%s" % sys.argv[1]
        sectionDoc.loadDocument(sys.argv[1])
    else:
        sectionDoc.loadDocument('C:/Users/glavaux/Shared/LITE/Ikonos/20090721222747_po_2627437_0000000/po_2627437_metadata.txt')

    sectionDoc.getValue('Product Order Area (Geographic Coordinates)', "Number of Coordinates")

    sectionDoc.getSectionLine('Map Projection:*')
    
        

if __name__ == "__main__":
    main()
