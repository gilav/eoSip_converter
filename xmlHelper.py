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

LXML_READY=False
try:
    import lxml.etree as etree
    LXML_READY=True
except:
    pass



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
    def getNodeChildrenByName(self, node=None, name=None):
        if node == None:
            raise Exception("node can not be None")
        result = []
        nodeList = node.childNodes
        for node in nodeList:
            if node.localName == name:
                result.append(node)
        if self.DEBUG!=0:
            print "  getNodeChildrenByName() return: %s items" % len(result)
        return result


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
            raise Exception("result list can not be None")
        
        if self.DEBUG==1:
            print ""
        if self.domDoc==None:
            raise Exception("dom document is None, is data parsed?")
        # need that path starts with /
        if len(path)>0 and path[0] != "/":
            path = "/" + path
        if self.DEBUG!=0:
            print "  getNodeByPath: current path:%s" % path

        # get root node by default
        if node == None:
            node = self.getRootNode()
            # already good?
            if self.DEBUG!=0:
                print "  getNodeByPath() test root node.localName:%s VS %s" % (node.localName, path)
            if "/"+node.localName==path:
                result.append(node)
                return
            
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
                    print "  getNodeByPath: non-deep-ok node[%d]; name:%s; currentLevel:%s" % (n, node.localName, currentLevel)
                if node.localName == currentLevel:
                    if self.DEBUG!=0:
                        print "  getNodeByPath: non-deep-ok node[%d] name:%s match" % (n, node.localName)
                    self.getNodeByPath(node, nextPath, attr, result)
                n=n+1

        else: #deepest ok level reached
            # look for the node
            nodeList = node.childNodes
            n=0
            for node in nodeList:
                if self.DEBUG!=0:
                    print "  getNodeByPath: deep-ok node[%d]; name:%s; currentLevel:%s" % (n, node.localName, currentLevel)
                if node.localName == currentLevel:
                    if self.DEBUG!=0:
                        print "  getNodeByPath: deep-ok node[%d] name:%s match" % (n, node.localName)
                    result.append(node)
                n=n+1

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
        #if node==None:
        #    return None
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
    # pretty print using minidom
    #
    def prettyPrint(self, node=None):
        if node==None:
            return self.domDoc.documentElement.toxml()
        else:
            return node.toxml()

    #
    # pretty print using minidom or lxml
    #
    def prettyPrintAll(self):
        global LXML_READY
        if not LXML_READY:
            if self.DEBUG!=0:
                print "use minidom"
            return self.domDoc.documentElement.toprettyxml()
        else:
            if self.DEBUG!=0:
                print "use LXML"
            parser = etree.XMLParser(resolve_entities=False, strip_cdata=False, remove_blank_text=True)
            document = etree.fromstring(self.data, parser)
            return etree.tostring(document, encoding='utf-8', pretty_print=True)


def main():
    """Main funcion"""

    helper=XmlHelper()
    if len(sys.argv) > 1:
        print "use xmlHelper on file:%s" % sys.argv[1]
        helper.loadFile(sys.argv[1])
        helper.parseData()
        print "info:%s" % helper.info()
        
        #helper.getNodeByName(None, "List_of_Ipf_Procs")
        #resultList=[]
        #helper.getNodeByPath(None, "Quality_Assesment/Quality_Parameter", None, resultList)
        #print "result 1:%s" % resultList
        #print "result 1 text :%s" % helper.getNodeText(resultList[0])

    else:
        path="C:/Users/glavaux/data/Development/python/xmls/KO2_OPER_EOC_PAN_1G_20110504T015124_20110504T015124_0001.XML"
        helper.loadFile(path)
        helper.parseData()
        helper.info()

        print "\n\nPretty print:\n%s" % helper.prettyPrintAll()
        #print "\n\nPretty print:\n%s" % helper.indentXmlAll()
        
if __name__ == "__main__":
    main()
