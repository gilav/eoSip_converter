import sys
current_module = sys.modules[__name__]

# def name
FIXED__PACKAGE_EXT='PACKAGE_EXT'
FIXED__EOSIP_PRODUCT_EXT='EOSIP_PRODUCT_EXT'
FIXED__JPEG_EXT='JPEG_EXT'
FIXED__PNG_EXT='PNG_EXT'
FIXED__XML_EXT='XML_EXT'
FIXED__SIP='SIP'

FIXED__BROWSE_JPEG_EXT='BROWSE_JPEG_EXT'
FIXED__BROWSE_PNG_EXT='BROWSE_PNG_EXT'
FIXED__MD_EXT='MD_EXT'
FIXED__QR_EXT='QR_EXT'
FIXED__SI_EXT='SI_EXT'
FIXED__REPORT_EXT='REPORT_EXT'


# fixed:
__PACKAGE_EXT='ZIP'
__EOSIP_PRODUCT_EXT='ZIP'
__JPEG_EXT='JPG'
__PNG_EXT='PNG'
__XML_EXT='XML'
__SIP='SIP'

# composed:
__BROWSE_JPEG_EXT='BI.%s' % __JPEG_EXT
__BROWSE_PNG_EXT='BI.%s' % __PNG_EXT
__MD_EXT='MD.%s' % __XML_EXT
__QR_EXT='QR.%s' % __XML_EXT
__SI_EXT='SI.%s' % __XML_EXT
__REPORT_EXT=__XML_EXT


#
# get a definition value
#
def getDefinition(name=None):
    if hasattr(current_module, "__%s" % name):
        return getattr(current_module, "__%s" % name)
    else:
        return "NO-EoSip-def:'%s'" % name
    
#
# returns the extension of the nth browse. add D if default
#
def getBrowseExtension(n=0, format=__BROWSE_JPEG_EXT, default=False ):
    result=''
    if n==0: # we only have one browse
        result = format
    else: # add D if the browse is the default one
        base=format
        pos = base.find('.')
        result=base[0:pos]
        if default==1:
            result="%sD" %result
        result="%s.browse%d" % (result, n)
        result="%s%s" % (result, base[pos+1:])
    #print " getBrowseExtension(%s) returns:%s" % (n, result)
    return result
        
        
