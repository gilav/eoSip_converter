#!/usr/bin/env python
#
# xml helper
# Lavaux Gilles 2013
#
#
import os
import sys
import xml.dom.minidom
import StringIO



class XmlHelper:
    # dom object
    domDoc = None
    # path
    path = None
    # data
    data=None
    #
    DEBUG=0
    
    def __init__(self):
        if self.DEBUG!=0:
            print "xmlHelper created"

            
    #
    # set debug
    #
    def setDebug(self, d=None):
        self.DEBUG=d
    #
    # get debug
    #
    def getDebug(self):
        return self.DEBUG
    

    #
    # set domDoc
    #
    def setDomDoc(self, d=None):
        self.domDoc = d

    #
    # get domDoc
    #
    def getDomDoc(self):
        return self.domDoc

        
    #
    # set content
    #
    def setData(self, d=None):
        self.data = d

    #
    # get rootNode
    #
    def getRootNode(self):
        return self.domDoc.documentElement
    

    #
    # load a file, don't parse the content
    #
    def loadFile(self, p=None):
        self.path=p
        if self.DEBUG!=0:
            print " will load file:%s" % self.path
        fd = open(self.path, 'r')
        self.rawLines = fd.readlines()
        fd.close()
        self.data = ''
        for item in self.rawLines:
            self.data = "%s%s" % (self.data, item)
        if self.DEBUG!=0:
            print "  %s loaded" % self.path


    #
    # parse content
    #
    def parseData(self, d=None):
        if d!=None:
            self.data=d
        if self.data == None or len(self.data) == 0:
            raise exception("nothing to be parsed")
        self.domDoc = xml.dom.minidom.parseString(self.data)
        if self.DEBUG!=0:
            print "  data parsed"


    #
    # get list of nodes by name
    #
    def getNodeByName(self, node=None, name=None):
        # get root node by default
        if node == None:
            node = self.domDoc.firstChild
        nodeList = node.childNodes
        result = []
        for node in nodeList:
            if node.localName == name:
                result.append(node)
        if self.DEBUG!=0:
            print "  getNodeByName() return: %s items" % len(result)


    #
    # get first node by path 
    #
    def getFirstNodeByPath(self, node=None, path=None, attr=None):
        result=[]
        self.getNodeByPath(node, path, attr, result)
        if len(result)>0:
            return result[0]
        else:
            return None

    #
    # get list of nodes by path
    #
    def getNodeByPath(self, node=None, path=None, result=[]):
        self.getNodeByPath(node, path, None, result)

    #
    # get list of nodes by path (TODO: and filter by attribute if given)
    #
    def getNodeByPath(self, node=None, path=None, attr=None, result=None):
        if result==None:
            raise Exception("result list is None")
        
        if self.DEBUG==1:
            print ""
        if self.domDoc==None:
            raise Exception("dom document is None, is data parsed?")
        # get root node by default
        if node == None:
            node = self.getRootNode()
        # need that path starts with /
        if len(path)>0 and path[0] != "/":
            path = "/" + path
        if self.DEBUG!=0:
            print "  getNodeByPath: current path:%s" % path
        # get current level name, build next iteration path
        toks=path.split("/")
        if self.DEBUG!=0:
            print "  getNodeByPath: toks:%s" % toks
        currentLevel=toks[1]
        nextPath=""
        if len(toks) > 2:
            for seg in  range(2, len(toks)):
                nextPath = "%s/%s" % (nextPath, toks[seg])
        if self.DEBUG!=0:
            print "  getNodeByPath: currentLevel:%s;  nextPath;%s" % (currentLevel, nextPath)

        if nextPath!='': # not deepest level
            # look for non leaf node
            nodeList = node.childNodes
            n=0
            for node in nodeList:
                if self.DEBUG!=0:
                    print "  getNodeByPath: non-leaf node[%d] name:%s" % (n, node.localName)
                if node.localName == currentLevel:
                    if self.DEBUG!=0:
                        print "  getNodeByPath: non-leaf node[%d] name:%s match" % (n, node.localName)
                    self.getNodeByPath(node, nextPath, attr, result)

        else: #deepest level reached
            # look for leaf node
            nodeList = node.childNodes
            n=0
            for node in nodeList:
                if self.DEBUG!=0:
                    print "  getNodeByPath: leaf node[%d] name:%s" % (n, node.localName)
                if node.localName == currentLevel:
                    if self.DEBUG!=0:
                        print "  getNodeByPath: leaf node[%d] name:%s match" % (n, node.localName)
                    result.append(node)

    #
    # info
    #
    def info(self):
        print "xmlHelper.info:"
        print " path:%s" % self.path
        if self.data != None:
            print " data length: %d" % len(self.data)
        else:
            print " data: None"


    #
    # get a node text content
    #
    def getNodeText(self, node):
        res = None
        n=0
        for anode in node.childNodes:
            n=n+1
            #print " child %d: type:%s  %s" % (n, anode.nodeType, anode)
            if anode.nodeType == anode.TEXT_NODE:
                res = anode.data
        return res

    #
    # get a node attribute text content
    #
    def getNodeAttributeText(self, node, attr):
        res = None
        #print " questo e il valore %d: type:%s  %s" % (None,node)
        res = node.getAttribute(attr)
        return res


    #
    # set a node text content
    #
    def setNodeText(self, node, text):
        res = None
        for anode in node.childNodes:
            if anode.nodeType == anode.TEXT_NODE:
                anode.data = text
                res=anode.data
        if res==None:
            textnode = self.domDoc.createTextNode(text)
            node.appendChild(textnode)
        return res


    #
    # pretty print
    #
    def prettyPrint(self, node=None):
        if node==None:
            return self.domDoc.documentElement.toxml()
        else:
            return node.toxml()


def main():
    """Main funcion"""

    helper=XmlHelper()
    if len(sys.argv) > 1:
        print "use xmlHelper on file:%s" % sys.argv[1]
        helper.loadFile(sys.argv[1])
        helper.parseData()
        print "info:%s" % helper.info()
        
        helper.getNodeByName(None, "List_of_Ipf_Procs")

        resultList=[]
        #helper.getNodeByPath(None, "Quality_Assesment/Quality_Parameter")
        helper.getNodeByPath(None, "Quality_Assesment/Quality_Parameter", None, resultList)
        print "result 1:%s" % resultList
        print "result 1 text :%s" % helper.getNodeText(resultList[0])

        #resultList=[]
        #helper.getNodeByPath(None, "List_of_Ipf_Procs/Ipf", None, resultList)
        #print "result 2:%s" % resultList
        

if __name__ == "__main__":
    main()
