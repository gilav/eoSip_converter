#
# EoSip convertion using distributed worker
#
# the work item, will contains the following info:
#  - id
#  - path of eoSip converter
#  - path of eoSip converter config file
#  - name of batch
#  - id of batch
#
#
# For Esa/lite dissemination project
#
# Serco 02014
# Lavaux Gilles 
#
# base on Pyro4 examples
#
# 21/09/2014: V: 0.1
#
#
#


#
# store the parameter needed by the worker then converter
#
class Workitem(object):
    def __init__(self, itemId, converterPath, configPath, products=None, batchName=None, batchId=None):
        print("Created workitem %s, converterPath=%s, configPath=%s, products=%s batchName=%s, batchId=%s" % (itemId, converterPath, configPath, products, batchName, batchId))
        self.itemId = itemId
        self.converterPath = converterPath
        self.configPath = configPath
        self.products = products
        self.batchName = batchName
        self.batchId = batchId
        # set by worker:
        self.processedBy=None
        self.result=None
        self.error=None
        self.numDone=-1
        self.numError=-1
        self.listDone=None
        self.listError=None

    def __str__(self):
        return "<Workitem id=%s>" % str(self.itemId)
