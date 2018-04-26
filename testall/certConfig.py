#!/usr/bin/evn python3

import json
import pprint
import util
import time
import sys
from collections import OrderedDict
from functools import partial

sys.path.insert(0, r'.\CertClient')
from CertClient import CertClient

logger = util.getLogger('certTest')
user_name = "Tissa"
cert_name = "netx_6.3"


class CertError(Exception):
    def __init__(self, value=0, message="Default CertError"):
        self.value = value
        self.message = message

    def __str__(self):
        return self.message


class CertTestConfig:
    ## TODO: it should be revised to a Singleton?
    def __init__(self, configFile='config.json'):
        self.configFile = configFile
        with open(self.configFile) as f:
            jsonData = f.read()
        self.json = json.loads(jsonData
                               # , object_pairs_hook=OrderedDict
                               )

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(self.json)


class Resource:
    resourceTracker = list()
    cfg = CertTestConfig()
    c = CertClient()

    @classmethod
    def _IXIA(cls, action="STATUS"):
        logger.info("_IXIA: "+action)
        """
        assert action == "ADD" or action == "REMOVE"
        test_bed_ip = cls.c.getipaddress()

        jobid = cls.c.requestIxia(
            cls.cfg.json["IXIA"]["user_name"], action,
            cls.cfg.json["IXIA"]["cert_name"], test_bed_ip)

        if jobid == 0:
            raise CertError(1, "IXIA resource allocation job id is 0.  Dispatcher crashed?")

        logger.info("IXIA resource allocation job id is {}".format(jobid))
        time.sleep(1)

        try:
            resp = cls.c.getJob(jobid)
            logger.info("The job {} status is {}.".format(jobid, resp['state']))
            if (resp and 'state' in resp and resp['state'] == 'WAITING'):
                # Wait for the job finis
                while (True):
                    if (cls.c.checkJobDone(jobid)):
                        logger.info("job {0} is done".format(jobid))
                        break;
                    else:
                        print('.', end='', flush=True)
                        time.sleep(30)
            else:
                logger.error("IXIA not available for ADD or REMOVE ")
        except (TypeError, ValueError) as e:
            logger.error("IXIA allocation error: ", e)
        """
        # cls.resourceTracker.append(partial(Resource._IXIA, "REMOVE"))

    @classmethod
    def _VM(cls, action, num_vm, num_intf):
        logger.info("_VM: "+action)

    @classmethod
    def preTestValidation(cls):
        logger.info("PreTestValidation")

    @classmethod
    def postTestValidation(cls):
        logger.info("postTestValidation")

    @classmethod
    def configure(cls):
        logger.info("Configuration")

    @classmethod
    def unconfigure(cls):
        logger.info("Un-Configuration")

    @classmethod
    def deploy(cls):
        logger.info("Resource Deploy")
        cls._IXIA("ADD")

    @classmethod
    def undeploy(cls):
        logger.info("Resource Undeploy")
        cls._IXIA("REMOVE")

    @classmethod
    def saveLog(cls):
        logger.info("Save Log file")


if __name__ == '__main__':
    pass
