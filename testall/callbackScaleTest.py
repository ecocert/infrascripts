#!/usr/bin/env python
import unittest
import util
import subprocess
from certConfig import Resource
from certConfig import CertTestConfig

logger = util.getLogger('certTest')


class CallbackScaleTest(unittest.TestCase):
    res = Resource("CallbackScaleTest")

    @classmethod
    def setUpClass(cls):
        try:
            logger.info("------------------------------------------")
            logger.info("set up the fixture for Callback Scale Test")
            cls.res.preTestValidation()
            cls.res.configure()
            cls.res.deployInfrastucture()
            cls.res.deployVM()
            cls.res.powerVM()
            logger.info("Press ENTER to continue...")
            input()
        except:
            cls.res.cleaner.pop_all().close()
            cls.res.saveLog()
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Callback Scale Test")
        cls.res.undeployAll()
        cls.res.saveLog()

    def _getAllVM_IPAddr(self):
        logger.info("_getAllVM_IPAddr")
        cmd = "C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe " \
              " -F ..\\testscripts\\CallbackScale362\\GetAllVM_IPAddr.ps1 "
        util.execPSCommand(cmd)

    def testConnectivity(self):
        logger.info("testConnectivity")
        ipAddr = '172.16.11.1'
        sshClient = util.ssh(ipAddr, "vmware", "VMware1!")
        output = sshClient.sendCommand("/home/vmware/ping_linux_vm.sh")
        logger.info('-' * 20)
        logger.info(output)

        self._getAllVM_IPAddr()

    def testCase2(self):
        self.assertTrue(False, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")
