#!/usr/bin/evn python3

import json
import pprint
import util
import time
import sys
import contextlib
import util

sys.path.insert(0, r'.\CertClient')
from CertClient import CertClient

logger = util.getLogger('certTest')
user_name = "Tissa"
cert_name = "netx_6.3"


class CertException(Exception):
    pass


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


class Resource(object):
    """
    _instance = None  # Singleton

    def __new__(cls, testName, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Resource, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    """

    def __init__(self, testName):
        self.cleaner = contextlib.ExitStack()
        self.cfg = CertTestConfig()
        self.c = CertClient()
        self.testName = testName

    def _IXIA(self, action="STATUS"):
        logger.info("_IXIA: " + action)
        # return (action, "WAITING")

        test_bed_ip = self.c.getipaddress()
        jobid = self.c.requestIxia(
            self.cfg.json["IXIA"]["user_name"], action,
            self.cfg.json["IXIA"]["cert_name"], test_bed_ip)

        if jobid == 0:
            raise CertException("IXIA resource allocation job id is 0.  Dispatcher crashed?")
        time.sleep(10)

        try:
            resp = self.c.getJob(jobid)
            logger.info("The job {} status is {}.".format(jobid, resp['state']))
            if (resp and 'state' in resp and resp['state'] == 'WAITING'):
                # Wait for the job finish
                while (True):
                    if (self.c.checkJobDone(jobid)):
                        logger.info("job {0} is done".format(jobid))
                        time.sleep(5)
                        break;
                    else:
                        # This is a hack, the state would change to 'CANCLED' for unknown reason
                        resp = self.c.getJob(jobid)
                        if resp and 'state' in resp and resp['state'] == 'CANCELED':
                            raise CertException("IXIA not available for {}".format(action))
                        print('.', end='', flush=True)
                        time.sleep(30)

                return (action, "WAITING")
            elif (resp and 'state' in resp and resp['state'] == 'CANCELED'):
                raise CertException("IXIA not available for {}".format(action))
            else:
                raise CertException("Unknown return status")

        except (TypeError, ValueError) as e:
            raise CertException("IXIA allocation error: ")

    def _powerIXIA(self, action):
        if action == "ON":
            psCmd = util.CmdTemplate.format("powerOnIxia")
        elif action == "OFF":
            psCmd = util.CmdTemplate.format("shutDownIxia")
        else:
            raise CertException("action = " + action)
        logger.info(psCmd)
        util.execPSCommand(psCmd)
        if action == "OFF":
            psCmd = util.CmdTemplate.format("deleteIxia")
            logger.info(psCmd)
            util.execPSCommand(psCmd)

    def _Infrastructure(self, action):
        logger.info("{} Infrastructure".format(action))
        if action == "SETUP":
            psCmd = util.CmdTemplate.format(
                "prepareInfra -perfClusterName \"{}\"".format(self.cfg.json["ClusterName"]))
        elif action == "CLEAR":
            psCmd = util.CmdTemplate.format(
                "clearInfraConfig -perfClusterName \"{}\"".format(self.cfg.json["ClusterName"]))
        else:
            raise CertException("action = " + action)
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    def _VM(self, action):
        logger.info("_VM: " + action)
        if action == "ADD":
            psCmd = util.CmdTemplate.format(
                "prepareVerticalScale -start {} -end {}".format(
                    self.cfg.json[self.testName]["startvm"],
                    self.cfg.json[self.testName]["endvm"]))
        elif action == "DELETE":
            psCmd = util.CmdTemplate.format(
                "deleteLinuxVMs -start {} -end {}".format(
                    self.cfg.json[self.testName]["startvm"],
                    self.cfg.json[self.testName]["endvm"]))
        else:
            raise CertException("action = " + action)
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    def _addInterfaceToVM(self):
        logger.info("addInterfaceToVM")
        print(self.testName)
        psCmd = util.CmdTemplate.format(
            "AddInterfacesToLinuxVM -start {} -end {} -numOfInf {} {}".format(
                self.cfg.json[self.testName]["startvm"],
                self.cfg.json[self.testName]["endvm"],
                self.cfg.json[self.testName]["numOfIntf"],
                self.cfg.json[self.testName]["VDSwithName"]))
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    def _removeInterfaceFromVM(self):
        logger.info("removeInterfaceFromVM")
        psCmd = util.CmdTemplate.format(
            "removeInterfacesFromLinuxVM -start {} -end {} -numOfInf {} {}".format(
                self.cfg.json[self.testName]["startvm"],
                self.cfg.json[self.testName]["endvm"],
                self.cfg.json[self.testName]["numOfIntf"],
                self.cfg.json[self.testName]["VDSwithName"]))
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    def configureIPAddr(self):
        logger.info("configureIPAddr")
        psCmd = util.CmdTemplate.format(
            "connectAndAddIP -start {} -end {}".format(
                self.cfg.json[self.testName]["startvm"],
                self.cfg.json[self.testName]["endvm"]))
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    def _powerVM(self, action):
        logger.info("_powerVM: " + action)
        if action == "ON":
            psCmd = util.CmdTemplate.format(
                "powerOnLinuxVM -start {} -end {}".format(
                    self.cfg.json[self.testName]["startvm"],
                    self.cfg.json[self.testName]["endvm"]))
        elif action == "OFF":
            psCmd = util.CmdTemplate.format(
                "shutDownLinuxVMs -start {} -end {}".format(
                    self.cfg.json[self.testName]["startvm"],
                    self.cfg.json[self.testName]["endvm"]))
        else:
            raise CertException("action = " + action)
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    def preTestValidation(self):
        logger.info("PreTestValidation")
        self.cleaner.callback(self.postTestValidation)

    def postTestValidation(self):
        logger.info("postTestValidation")

    def configure(self):
        logger.info("Configuration")
        self.cleaner.callback(self.unconfigure)

    def unconfigure(self):
        logger.info("Un-Configuration")

    def deployIxia(self):
        action, status = self._IXIA("ADD")
        if action == "ADD" and status == "WAITING":
            self.cleaner.callback(self._IXIA, "REMOVE")

    def powerOnIXIA(self):
        self._powerIXIA("ON")
        self.cleaner.callback(self._powerIXIA, "OFF")

    def deployInfrastucture(self):
        self._Infrastructure("SETUP")
        self.cleaner.callback(self._Infrastructure, "CLEAR")

    def deployVM(self):
        self._VM("ADD")
        self.cleaner.callback(self._VM, "DELETE")

    def powerVM(self):
        self._powerVM("ON")
        self.cleaner.callback(self._powerVM, "OFF")

    def addIfToVM(self):
        self._addInterfaceToVM()
        self.cleaner.callback(self._removeInterfaceFromVM)

    def undeployAll(self):
        logger.info("Resource Undeploy")
        self.cleaner.close()

    def saveLog(self):
        logger.info("Save Log file")


if __name__ == '__main__':
    pass
