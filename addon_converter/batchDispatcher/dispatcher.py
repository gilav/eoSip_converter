#
# EoSip convertion using distributed worker
#
# the dispatcher:
#  pyro server that implements a working queue.
#  several worker(s) will pull job for it, process it and put back results
#  one client will set the list of job to be done
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
from __future__ import print_function

try:
    import queue
except ImportError:
    import Queue as queue
import Pyro4

# we're using custom classes, so need to use pickle
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')


class DispatcherQueue(object):
    def __init__(self):
        self.workqueue = queue.Queue()
        self.resultqueue = queue.Queue()

    def putWork(self, item):
        self.workqueue.put(item)

    def getWork(self, timeout=5):
        return self.workqueue.get(block=True, timeout=timeout)

    def putResult(self, item):
        self.resultqueue.put(item)

    def getResult(self, timeout=5):
        return self.resultqueue.get(block=True, timeout=timeout)

    def workQueueSize(self):
        return self.workqueue.qsize()

    def resultQueueSize(self):
        return self.resultqueue.qsize()

# main program

Pyro4.Daemon.serveSimple({
    DispatcherQueue(): "eosip.converter.dispatcher"
})
