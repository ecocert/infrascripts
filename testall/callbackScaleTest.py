#!/usr/bin/env python
import unittest
import util
import subprocess
from certConfig import Resource
from certConfig import CertTestConfig

logger = util.getLogger('certTest')


class CallbackScaleTest(unittest.TestCase):
    res = Resource()

    @classmethod
    def setUpClass(cls):
        logger.info("------------------------------------------")
        logger.info("set up the fixture for Callback Scale Test")
        cls.res.preTestValidation()
        cls.res.configure()

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Callback Scale Test")
        cls.res.undeployAll()
        Resource.saveLog()

    def testCase1(self):
        self.assertTrue(True, "assertTrue")

    def testCase2(self):
        self.assertTrue(False, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")