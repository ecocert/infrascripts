#!/usr/bin/evn python3

import json
import pprint
import util
import time
import sys
import contextlib
import util
import os
import multiprocessing

sys.path.insert(0, r'.\CertClient')
sys.path.insert(0, r'.\CallbackScale362')
from CertClient import CertClient
from CallbackScaleUtils import CallbackScale

logger = util.getLogger('certTest')


# user_name = "Tissa"
# cert_name = "netx_6.3"


class CertException(Exception):
    pass


class CertJsonConfig:
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


class Resource():
    def __init__(self, testName):
        self.cb = CallbackScale()
        self.cleaner = contextlib.ExitStack()
        self.cfg = CertJsonConfig()
        self.c = CertClient()
        self.testName = testName

    #  resource = "IXIA" or "ESX"
    #  action = "ADD", "REMOVE" or "STATUS"
    def _resourceAllocDispatcher(self, resource, action="STATUS"):
        logger.info("_resourceAllocDispatcher {} {}".format(resource, action))
        # return (action, "WAITING")

        test_bed_ip = self.c.getipaddress()
        if resource == "IXIA":
            jobid = self.c.requestIxia(
                self.cfg.json["Dispatcher"]["user_name"], action,
                self.cfg.json["Dispatcher"]["cert_name"], test_bed_ip)
        elif resource == "ESX":
            jobid = self.c.requestScale(
                self.cfg.json["Dispatcher"]["user_name"], action,
                self.cfg.json["Dispatcher"]["cert_name"], test_bed_ip)
        else:
            raise CertException("param error: action={}".format(action))

        if jobid == 0:
            raise CertException("resource allocation job id is 0.  Dispatcher crashed?")

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
                            raise CertException("{} not available for {}".format(resource, action))
                        print('.', end='', flush=True)
                        time.sleep(30)

                return (action, "WAITING")
            elif (resp and 'state' in resp and resp['state'] == 'CANCELED'):
                raise CertException("{} not available for {}".format(resource, action))
            else:
                raise CertException("Unknown return status")
        except (TypeError, ValueError) as e:
            raise CertException("{} {} error.".format(resource, action))

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

    def _cbScaleSetup(self):
        logger.info("Callback Scale Setup")
        rc = False
        in_fname = os.getcwd() + "\\CallbackScale362\\" + self.cfg.json["CallbackScaleTest"]["INPUT_PATH"] + \
                   self.cfg.json["CallbackScaleTest"]["GVM_INPUT_FNAME"]
        if not os.path.isfile(in_fname):
            print("WARN : FILE DOES NOT EXISTS " + in_fname)
            return False

        cb_scale_count = self.cfg.json["CallbackScaleTest"]["SCALE_COUNT_TOTAL"]
        rc = self.cb.cb_scale_config_setup(in_fname, cb_scale_count)
        if rc == False:
            logger.error("Callback Scale Setup error")

    def _cbScaleCleanup(self):
        logger.info("Callback Scale Cleanup")
        rc = False
        rc = self.cb.cb_scale_config_cleanup()
        if rc == False:
            logger.error("Callback Scale Cleanup error")

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
        action, status = self._resourceAllocDispatcher("IXIA", "ADD")
        if action == "ADD" and status == "WAITING":
            self.cleaner.callback(self._resourceAllocDispatcher, "REMOVE")

    def deployESX(self):
        action, status = self._resourceAllocDispatcher("ESX", "ADD")
        if action == "ADD" and status == "WAITING":
            self.cleaner.callback(self._resourceAllocDispatcher, "REMOVE")

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

    def cbScaleSetup(self):
        cmd = "C:/WINDOWS/system32/WindowsPowerShell/v1.0/powershell.exe " \
              " -F ./CallbackScale362/GetAllVM_IPAddr.ps1 "
        util.execPSCommand(cmd)
        self._cbScaleSetup()
        self.cleaner.callback(self._cbScaleCleanup)

    def _horizontalPing(self):
        logger.info("_horizontalPing")

    def horizontalSetup(self):
        startesx = self.cfg.json["HorizontalScaleTest"]["startesx"]
        endesx   = self.cfg.json["HorizontalScaleTest"]["endesx"]
        startvm  = self.cfg.json["HorizontalScaleTest"]["startvm"]
        endvm    = self.cfg.json["HorizontalScaleTest"]["endvm"]
        startnas = self.cfg.json["HorizontalScaleTest"]["startnas"]
        endnas   = self.cfg.json["HorizontalScaleTest"]["endnas"]
        startcluster = self.cfg.json["HorizontalScaleTest"]["startcluster"]
        endcluster   = self.cfg.json["HorizontalScaleTest"]["endcluster"]


        cmd_pfx = "C:/WINDOWS/system32/WindowsPowerShell/v1.0/powershell.exe " \
              " -F ./scalescripts/"


        #cmd = cmd_pfx + "pingHorizontalHosts.ps1"
        #util.execPSCommand(cmd)

        # Step 2
        cmd = cmd_pfx + "poweronScaleHosts.ps1 -start {} -end {}".format(startesx, endesx)
        util.execPSCommand(cmd)
        cmd = cmd_pfx + "shutdownScaleHosts.ps1 -start {} -end {}".format(startesx, endesx)
        self.cleaner.callback(util.execPSCommand, cmd)
        time.sleep(240)

        # Step 3
        cmd = cmd_pfx + "addScaleHostsIntovCenter.ps1 -start {} -end {}".format(startesx, endesx)
        util.execPSCommand(cmd)
        cmd = cmd_pfx + "removeScaleHostsFromvCenter.ps1 -start {} -end {}".format(startesx, endesx)
        self.cleaner.callback(util.execPSCommand, cmd)

        # Step 4
        cmd = cmd_pfx + "registerScaleVMsIntovCenter.ps1 -start {} -end {}".format(startvm, endvm)
        util.execPSCommand(cmd)
        cmd = cmd_pfx + "unregisterVMsFromvCenter.ps1 -start {} -end {}".format(startvm, endvm)
        self.cleaner.callback(util.execPSCommand, cmd)
        time.sleep(30)

        # Step 5
        cmd = cmd_pfx + "addScaleHostsToVDS.ps1 -start {} -end {}".format(startesx, endesx)
        util.execPSCommand(cmd)
        cmd = cmd_pfx + "removeScaleHostsFromVDS.ps1 -start {} -end {}".format(startesx, endesx)
        self.cleaner.callback(util.execPSCommand, cmd)
        time.sleep(15)

        logger.info("Press ENTER to continue...")
        input()

        # Step 6
        """
        for nas in range(startnas, endnas+1):
            cmd = cmd_pfx + "freeNASRestClient.ps1 -index {} -action {}".format(nas, 1)
            util.execPSCommand(cmd)
            cmd = cmd_pfx + "freeNASRestClient.ps1 -index {} -action {}".format(nas, 2)
            self.cleaner.callback(util.execPSCommand, cmd)
        

        # Step 7
        cmd = cmd_pfx + "storageScanOnScaleHosts.ps1 -start {} -end {}".format(startesx, endesx)
        util.execPSCommand(cmd)
        """

        """
        # Step 12
        cmd = cmd_pfx + "powerOnLinuxVMs.ps1 -start {} -end {}".format(startvm, endvm)
        util.execPSCommand(cmd)
        cmd = cmd_pfx + "shutdownLinuxVMs.ps1 -start {} -end {}".format(startvm, endvm)
        self.cleaner.callback(util.execPSCommand, cmd)
        """

        # Step 14
        for i in range(startcluster, endcluster+1):
            cmd = cmd_pfx + "NSXHostPreparationInstallation.ps1 -index {} -method \"POST\" ".format(i)
            util.execPSCommand(cmd)
            cmd = cmd_pfx + "NSXHostPreparationInstallation.ps1 -index {} -method \"DELETE\" ".format(i)
            self.cleaner.callback(util.execPSCommand, cmd)
            time.sleep(1)

        # Step 15
        for i in range(startcluster, endcluster + 1):
            cmd = cmd_pfx + "NSXServiceDeployment.ps1 -index {} -method \"POST\" ".format(i)
            util.execPSCommand(cmd)
            cmd = cmd_pfx + "NSXServiceDeployment.ps1 -index {} -method \"DELETE\" ".format(i)
            self.cleaner.callback(util.execPSCommand, cmd)
            time.sleep(1)

        # Step 16
        for i in range(startcluster, endcluster + 1):
            cmd = cmd_pfx + "NSXServiceDeploymentStatus.ps1 -index {} -servicename \"Guest Introspection\" ".format(i)
            util.execPSCommand(cmd)

        # Create security group and security policies
        self.cbScaleSetup()


    def undeployAll(self):
        logger.info("Resource Undeploy")
        self.cleaner.close()

    def saveLog(self):
        logger.info("Save Log file")


if __name__ == '__main__':
    pass
