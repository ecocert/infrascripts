#!/usr/bin/env python
import unittest
import util
import subprocess
from certConfig import Resource
from certConfig import CertTestConfig

logger = util.getLogger('certTest')


class VerticalScaleTest(unittest.TestCase):
    config = CertTestConfig()

    @classmethod
    def setUpClass(cls):
        logger.info("set up the fixture for Vertical Scale Test")
        Resource.preTestValidation()
        Resource.configure()
        # Resource.deploy()
        psCmd = util.CmdTemplate.format("prepareInfra -$perfClusterName \"{}\"".format(cls.config.json["ClusterName"]))
        logger.info(psCmd)
        util.execPSCommand(psCmd)

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Vertical Scale Test")
        psCmd = util.CmdTemplate.format(
            "clearInfraConfig -$perfClusterName \"{}\"".format(cls.config.json["ClusterName"]))
        logger.info(psCmd)
        util.execPSCommand(psCmd)
        # Resource.undeploy()
        Resource.postTestValidation()
        Resource.saveLog()

    def testCase1(self):
        self.assertTrue(True, "assertTrue")

    def testCase2(self):
        self.assertTrue(False, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")
