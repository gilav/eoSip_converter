import urllib
import urllib2


debug = False

#
# classe that can perform http GET and POST calls 
#
#
#

from service import Service

class HttpCall(Service):

    #
    #
    #
    def init(self, p=None):
        self.properties=p
        if debug:
            print " set service properties to:%s" % self.properties
        self.my_init()

    #
    #
    #
    def my_init(self, proxy=0, timeout=5):
        self.timeout=timeout
        self.request=None
        self.url=None
        self.params=None
        self.postData=None
        self.encodedParams=None
        self.proxy=None
        self.opener=None

        if proxy==0:
            if debug:
                print " disabling proxy"
            proxy_handler = urllib2.ProxyHandler({})
            self.opener = urllib2.build_opener(proxy_handler)
            #urllib2.install_opener(self.opener)
            if debug:
                print " proxy disabled"



    #
    #
    #
    def getproperties(self):
        return self.properties


    #
    #
    #
    def processRequest(self, url, data):
        return self.retrieveUsingPost(url, data)
    

    #
    # perform GET 
    # - u is URL path
    # - paramsa are params
    # - p is proxies
    #
    def retrieveUsingGet(self, u, p="", pr=None):
        self.url=u
        self.params=p
        self.proxy=pr
        if debug:
            print " will do GET: url=%s; params=%s;" % (self.url, self.params)
        self.encodedParams = urllib.quote(self.params)
        if debug:
            print " encodedParams=%s" % (self.encodedParams)
        self.request = urllib2.Request(url="%s?%s" % (self.url, self.params))
        if self.opener==None:
            if debug:
                print " use default proxy"
            f = urllib2.urlopen(self.request, timeout = self.timeout)
        else:

            if debug:print " dont use proxy"
            f = self.opener.open(self.request, timeout = self.timeout)
        return f.read().decode()
    
        
    #
    # perform POST
    # - u is URL path
    # - paramsa are params
    # - p is proxies
    #
    def retrieveUsingPost(self, u, d="", pr=None):
        self.url=u
        self.postData=d
        self.proxy=pr
        if debug:
            print " will do POST: url=%s; params=%s;" % (self.url, self.params)
        self.request = urllib2.Request(url=self.url)
        self.request.add_data(self.postData)
        if self.opener==None:
            if debug:
                print " use default proxy"
            f = urllib2.urlopen(self.request, timeout = self.timeout)
        else:
            if debug:
                print " don't use proxy"
            f = self.opener.open(self.request, timeout = self.timeout)
        return f.read().decode()

    #
    def info(self):
        result="HttpCall; url:"+self.url




if __name__ == '__main__':
    a="C:/Users/glavaux/Shared/LITE/spaceTmp/batch_tropforest_tropforest_workfolder_0/AL1_OPER_AV2_OBS_11_20090517T025758_20090517T025758_000000_E113_N000/AL1_OPER_AV2_OBS_11_20090517T025758_20090517T025758_000000_E113_N000.MD.XML"
    b = "C:/Users/glavaux/LITE/OGC_Schemas/opt.xsd";
    data="XML_PATH=%s&XSD_PATH=%s" % (a,b)
    dataBad="XSD_PATH=%s" % (b)

    #print f.read(1000)
    call = HttpCall()

    # GET
    print "\nSHOULD BE OK:"
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7002/validate", data)
    
    print "\nSHOULD BE BAD:"
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7002/validate", dataBad)
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7002/validate1", data)

    # POST
    print "\n\n\n\nSHOULD BE OK:"
    print "returned:%s" % call.retrieveUsingPost("http://127.0.0.1:7002/validate", data)

    print "\nSHOULD BE BAD:"
    print "returned:%s" % call.retrieveUsingPost("http://127.0.0.1:7002/validate", dataBad)
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7002/validate1", data)




