# WMCore dependecies here
from WMCore.REST.Server import RESTEntity, restcall
from WMCore.REST.Validation import validate_str

# CRABServer dependecies here
from CRABInterface.RESTExtensions import authz_login_valid
from CRABInterface.Regexps import RX_SUBRES_SI
from CRABInterface.Utils import conn_handler
from CRABInterface.__init__ import __version__

import HTCondorLocator
from TaskWorker.WorkerExceptions import TaskWorkerException

class RESTServerInfo(RESTEntity):
    """REST entity for workflows and relative subresources"""

    def __init__(self, app, api, config, mount, serverdn, centralcfg):
        RESTEntity.__init__(self, app, api, config, mount)
        self.centralcfg = centralcfg
        self.serverdn = serverdn
        #used by the client to get the url where to update the cache (cacheSSL)
        #and by the taskworker Panda plugin to get panda urls

    def validate(self, apiobj, method, api, param, safe ):
        """Validating all the input parameter as enforced by the WMCore.REST module"""
        authz_login_valid()
        if method in ['GET']:
            validate_str('subresource' , param, safe, RX_SUBRES_SI, optional=False)

    @restcall
    def get(self, subresource , workflowname = None):
        """Retrieves the server information, like delegateDN, filecacheurls ...
           :arg str subresource: the specific server information to be accessed;
        """
        return getattr(RESTServerInfo, subresource)(self)

    @conn_handler(services=['centralconfig'])
    def delegatedn(self):
        yield {'services': self.centralcfg.centralconfig['delegate-dn']}

    @conn_handler(services=['centralconfig'])
    def backendurls(self):
        yield self.centralcfg.centralconfig['backend-urls']

    @conn_handler(services=['centralconfig'])
    def version(self):
        yield self.centralcfg.centralconfig['compatible-version']+[__version__]

    @conn_handler(services=['centralconfig'])
    def scheddaddress(self, workflowname):

        try:
            loc = HTCondorLocator.HTCondorLocator(self.backendurls)
            schedd, address = loc.getScheddObj(workflowname)
        except:
            raise TaskWorkerException("Unable to get schedd address for task %s" % (workflowname))
            yield loc.scheddAd['Machine']

    @conn_handler(services=['centralconfig'])
    def bannedoutdest(self):
        yield self.centralcfg.centralconfig['banned-out-destinations']
