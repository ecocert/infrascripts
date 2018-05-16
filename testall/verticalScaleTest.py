#!/usr/bin/env python
import unittest
import util
import time
from certConfig import Resource

logger = util.getLogger('certTest')


class VerticalScaleTest(unittest.TestCase):
    res = Resource("VerticalScaleTest")

    @classmethod
    def setUpClass(cls):
        logger.info("------------------------------------------")
        logger.info("set up the fixture for Vertical Scale Test")
        try:
            cls.res.preTestValidation()
            cls.res.configure()
            cls.res.deployIxia()
            time.sleep(30)
            cls.res.deployInfrastucture()
            cls.res.powerOnIXIA()
            time.sleep(30)
            cls.res.deployVM()
            cls.res.addIfToVM()
            cls.res.powerVM()
            cls.res.configureIPAddr()
            #logger.info("Setup for Vertical Scale Test is ready. Press ENTER to continue...")
            #input()
        except:
            cls.res.cleaner.pop_all().close()
            cls.res.saveLog()
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Vertical Scale Test")
        cls.res.undeployAll()
        cls.res.saveLog()

    def testPingLinuxVM(self):
        logger.info("testPingLinuxVM")
        ipAddr = '172.16.11.1'
        sshClient = util.ssh(ipAddr, "vmware", "VMware1!")
        output = sshClient.sendCommand("/home/vmware/ping_linux_vm.sh")
        logger.info('-'*20)
        logger.info(output)
        # add assertion on ouput
    def testCase2(self):
        self.assertTrue(True, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")


