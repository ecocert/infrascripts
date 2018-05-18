#!/usr/bin/env python
import unittest
from certConfig import *

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
            cls.res.deployIxia()
            time.sleep(30)
            cls.res.deployInfrastucture()
            cls.res.powerOnIXIA()
            time.sleep(30)
            cls.res.deployVM()
            cls.res.powerVM()
            cls.res.cbScaleSetup()
            # logger.info("Press ENTER to continue...")
            # input()
        except:
            cls.res.cleaner.pop_all().close()
            cls.res.saveLog()
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Callback Scale Test")
        cls.res.undeployAll()
        cls.res.saveLog()

    def testConnectivity(self):
        logger.info("testConnectivity")
        ipAddr = r'172.16.11.1'
        sshClient = util.ssh(ipAddr, "vmware", "VMware1!")
        output = sshClient.sendCommand("/home/vmware/ping_linux_vm.sh")
        logger.info('-' * 20)
        logger.info(output)

    def testCase2(self):
        self.assertTrue(False, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")
