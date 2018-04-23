#!/usr/bin/env python

import unittest
import util
from certConfig import Resource

logger = util.getLogger('certTest')


class PerformanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("set up the fixture for Performance Test")
        # assert False, "set up fail"
        Resource.preTestValidation()
        Resource.configure()
        # Resource.deploy()

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Performance Test")
        # Resource.undeploy()
        Resource.postTestValidation()
        Resource.saveLog()

    def testCase1(self):
        self.assertTrue(True, "assertTrue")

    def testCase2(self):
        self.assertTrue(False, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")
