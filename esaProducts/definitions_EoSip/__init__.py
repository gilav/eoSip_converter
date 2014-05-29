import sys
current_module = sys.modules[__name__]


__PRODUCT_EXT='ZIP'
__JPEG_EXT='JPG'
__BROWSE_JPEG_EXT='BI.%s' % __JPEG_EXT
__PNG_EXT='PNG'
__BROWSE_PNG_EXT='BI.%s' % __PNG_EXT
__XML_EXT='XML'
__MD_EXT='MD.%s' % __XML_EXT
__QR_EXT='QR.%s' % __XML_EXT
__SI_EXT='SI.%s' % __XML_EXT
__PACKAGE_EXT='ZIP'
__REPORT_EXT=__XML_EXT


#
# get a definition value
#
def getDefinition(name=None):
    if hasattr(current_module, "__%s" % name):
        return getattr(current_module, "__%s" % name)
    else:
        return "NO-EoSip-def:%s" % name
    
#
# returns the extension of the nth browse 
#
def getBrowseExtension(n=0, default=None, format=__BROWSE_JPEG_EXT):
    result=''
    if n==0:
        #result = __BROWSE_JPEG_EXT
        result = format
    else:
        #base=__BROWSE_JPEG_EXT
        base=format
        pos = base.find('.')
        result=base[0:pos]
        if default==1:
            result="%sD" %result
        result="%s.browse%d" % (result, n)
        result="%s%s" % (result, base[pos+1:])
    #print " getBrowseExtension(%s) returns:%s" % (n, result)
    return result
        
        
