#!/usr/bin/env python
#
# file helper
# Lavaux Gilles 2013
#
#
import os
import time
import sys
import re
from os import walk
from os.path import splitext, join



class fileHelper:
    scanned=0
    DEBUG=0
    def __init__(self):
        if self.DEBUG!=0:
            print "fileHelper created"


    #
    #
    #
    def select_files(self, root, files, nameFilter=None, extFilter=None):

        #sys.stdout.write(" current path:%s                                                 \r" % root)
        selected_filesPath = []

        for file in files:
            self.scanned=self.scanned+1
            #do concatenation here to get full path 
            full_path = join(root, file)
            if self.DEBUG!=0:
                print "  full_path:%s" % full_path
            ext = splitext(file)[1]
            name = splitext(file)[0]

            ok=1
            if nameFilter != None:
                rs=nameFilter.match(name)
                #print "  re result:%s" % rs
                if rs==None:
                    ok=0
                    continue
                
            if extFilter != None:
                rs=extFilter.match(ext)
                #print "  re result:%s" % rs
                if rs==None:
                    ok=0
                    continue

            if ok:
                selected_filesPath.append(full_path)

        return selected_filesPath


    #
    # params:
    #  root: root path
    #  dirs: list of dirs (string)
    #  dirFilter: regex (re) compiled filter
    #  isLeaf: is the folder terminal
    #  isEmpty: 
    #
    def select_dirs(self, root, dirs, dirFilter=None, isLeaf=None, isEmpty=None):

        if self.DEBUG!=0:
            print " select_dirs root:%s" % root
            print "             dirs:%s" % dirs
            print "             dirFilter:%s" % dirFilter
            print "             isLeaf:%s" % isLeaf
            print "             isEmpty:%s" % isEmpty
            
        selected_dirPath = []

        for dir in dirs:
            self.scanned=self.scanned+1
            #do concatenation here to get full path 
            full_path = join(root, dir)
            if self.DEBUG!=0:
                print "  full_path:%s" % full_path

            ok=1
            if dirFilter != None:
                rs=dirFilter.match(dir)
                #print "  re result:%s" % rs
                if rs==None:
                    ok=0
                    if self.DEBUG!=0:
                        print "   --> not ok because of name re"
                    continue

            # test on isLeaf: test if there is subdir
            childs = os.listdir(full_path)
            if isLeaf!=None and isLeaf==1:
                for item in childs:
                    empty=0
                    if os.path.isdir(os.path.join(full_path, item)):
                        ok=0
                        if self.DEBUG!=0:
                            print "   --> not ok because of isleaf"
                        continue
                    
            # test on isEmpty
            if isEmpty!=None and isEmpty==1 and len(childs)!=0:
                ok=0
                if self.DEBUG!=0:
                    print "   --> not ok because of isEmpty has to be 1"
                continue

            if isEmpty!=None and isEmpty==0 and len(childs)==0:
                ok=0
                if self.DEBUG!=0:
                    print "   --> not ok because of isEmpty has to be 0"
                continue

            if ok:
                selected_dirPath.append(full_path)
                
        return selected_dirPath


    #
    # get recursive list of files
    #
    def list_files(self, path, nameFilter=None, extFilter=None):
        self.scanned=0
        if self.DEBUG!=0:
            print ""
            print " list_files: path=%s;  nameFilter=%s;  extFilter=%s" % (path, nameFilter, extFilter)
        selected_files = []

        if os.path.exists(path):
            for root, dirs, files in walk(path):
                selected_files += self.select_files(root, files, nameFilter, extFilter)
        else:
            raise Exception("path does not exists:%s" % path)

        return selected_files


    #
    # get recursive list of dir
    #
    def list_dirs(self, path, dirFilter=None, isLeaf=None, isEmpty=None):
        self.scanned=0
        if self.DEBUG!=0:
            print ""
            print " list_dirs: path=%s;  dirFilter=%s;  isLeaf=%s;  inEmpty=%s" % (path, dirFilter, isLeaf, isEmpty)
        selected_dir = []

        if os.path.exists(path):
            for root, dirs, files in walk(path):
                selected_dir += self.select_dirs(root, dirs, dirFilter, isLeaf, isEmpty)
        else:
            raise Exception("path does not exists:%s" % path)
        
        return selected_dir

    #
    # return the basename of a file (remove the path)
    #
    def basename(self, path):
        pos = path.rfind('/')
        if pos > 0:
            return path[pos+1:]
        else:
            return path

    #
    # return the dirname of a file (the path)
    #
    def dirname(self, path):
        pos = path.rfind('/')
        if pos > 0:
            return path[0:pos]
        else:
            return None
        
    #
    # return the extension for a filename/fullPath
    #
    def getFileExtension(self, path):
        pos = path.rfind('.')
        if pos > 0:
            return path[(pos+1):]
        else:
            return None

    #
    # remove the extension for a filename/fullPath
    #
    def removeFileExtension(self, path):
        pos = path.rfind('.')
        if pos > 0:
            return path[0:pos]
        else:
            return path


    #
    # set debug flag
    #
    def setDebug(self, b):
        self.DEBUG=b


def main():
    """Main funcion"""

    helper=fileHelper()


    a='C:/Users/glavaux/Shared/LITE/testData/Aeolus/ADM/1B/AE_TEST_ALD_U_N_1B_20101002T000000059_000936000_017071_0001.DBL'
    print "basename of:%s" % a
    print " ==>%s" % helper.basename(a)
    print "dirname of:%s" % a
    print " ==>%s" % helper.dirname(a)
    sys.exit(1)

    
    if len(sys.argv) > 1:
        print "use fileHelper on path:%s" % sys.argv[1]
    #
        #reProg = re.compile("^LS__PROD_RPT___.*")
        #re1Prog = re.compile("^VEGA.*")
        #re2Prog = re.compile("^.doc")
    #
    reProg=None
    re1Prog=None
    re2Prog=None
    start=time.time()
    list=helper.list_files(sys.argv[1], re1Prog, re2Prog)
    #list=helper.list_dirs(sys.argv[1], reProg, 1, 0)
    stop=time.time()
    print ""
    print "num of result:%d" % len(list)
    print "done in %f sec, scanned:%d" % ((stop-start), helper.scanned)
    #print "result:%s" % list
        

if __name__ == "__main__":
    main()
