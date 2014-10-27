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
    SETTING_TIMEOUT='TIMEOUT'


    #
    # class init
    # call super class
    #
    def __init__(self, name=None):
        Service.__init__(self, name)


    #
    # init
    # call super class
    #
    # param: p is usually the path of a property file
    #
    def init(self, p=None, ingester=None):
        Service.init(self, p, ingester)
        self.my_init()


    #
    # init done after the properties are loaded
    # do:
    # - check if DEBUG option set
    # - handle proxy + timeout options
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

        # DEBUG setting
        if self.getProperty(self.SETTING_DEBUG)!=None:
            print "@@@@@@@@@@@@@@@@@@ DEBUG setting:%s" % self.getProperty(self.SETTING_DEBUG)
            if self.getProperty(self.SETTING_DEBUG)=="true":
                self.debug=True

        # TIMEOUT setting
        if self.getProperty(self.SETTING_TIMEOUT)!=None:
            print "@@@@@@@@@@@@@@@@@@ TIMEOUT setting:%s" % self.getProperty(self.SETTING_TIMEOUT)
            self.timeout = int(self.getProperty(self.SETTING_TIMEOUT))

        if proxy==0:
            if self.debug:
                print " disabling proxy"
            proxy_handler = urllib2.ProxyHandler({})
            self.opener = urllib2.build_opener(proxy_handler)
            if self.debug:
                print " proxy disabled"


    #
    #
    #
    def processRequest(self, url, data):
        print "@@@@@@@@@@@@@@@@@@ processRequest, timeout=%d" % self.timeout
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
        if self.debug:
            print " will do GET: url=%s; params=%s;" % (self.url, self.params)
        self.encodedParams = urllib.quote(self.params)
        if self.debug:
            print " encodedParams=%s" % (self.encodedParams)
        self.request = urllib2.Request(url="%s?%s" % (self.url, self.params))
        if self.opener==None:
            if self.debug:
                print " use default proxy"
            f = urllib2.urlopen(self.request, timeout = self.timeout)
        else:

            if self.debug:
                print " dont use proxy"
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
        if self.debug:
            print " will do POST: url=%s; params=%s;" % (self.url, self.params)
        self.request = urllib2.Request(url=self.url)
        self.request.add_data(self.postData)
        if self.opener==None:
            if self.debug:
                print " use default proxy"
            f = urllib2.urlopen(self.request, timeout = self.timeout)
        else:
            if self.debug:
                print " don't use proxy"
            f = self.opener.open(self.request, timeout = self.timeout)
        return f.read().decode()

    #
    def info(self):
        result="HttpCall; url:"+self.url




if __name__ == '__main__':
    a="C:/Users/glavaux/Shared/LITE/spaceTmp/SP1_OPER_HRV1_X__1P_19881009T114531_19881009T114540_000029_0022_0322.MD_before.XML"
    b = "C:/Users/glavaux/LITE/OGC_Schemas/opt.xsd";
    data="XML_PATH=%s&XSD_PATH=%s" % (a,b)
    dataBad="XSD_PATH=%s" % (b)

    #print f.read(1000)
    call = HttpCall()
    call.init()

    # GET
    print "\nSHOULD BE OK:"
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7000/validate", data)
    
    print "\nSHOULD BE BAD:"
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7000/validate", dataBad)
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7000/validate1", data)

    # POST
    print "\n\n\n\nSHOULD BE OK:"
    print "returned:%s" % call.retrieveUsingPost("http://127.0.0.1:7000/validate", data)

    print "\nSHOULD BE BAD:"
    print "returned:%s" % call.retrieveUsingPost("http://127.0.0.1:7000/validate", dataBad)
    print "returned:%s" % call.retrieveUsingGet("http://127.0.0.1:7000/validate1", data)




