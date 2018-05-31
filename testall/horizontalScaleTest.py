#!/usr/bin/env python
import unittest
import util
from certConfig import Resource

logger = util.getLogger('certTest')


class HorizontalScaleTest(unittest.TestCase):
    res = Resource("HorizontalScaleTest")

    @classmethod
    def setUpClass(cls):
        logger.info("--------------------------------------------")
        logger.info("set up the fixture for Horizontal Scale Test")
        try:
            cls.res.preTestValidation()
            cls.res.configure()
            #cls.res.deployESX()
            cls.res.horizontalSetup()
            logger.info("Press ENTER to continue...")
            input()
        except:
            cls.res.cleaner.pop_all().close()
            cls.res.saveLog()
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Horizontal Scale Test")
        cls.res.undeployAll()
        cls.res.saveLog()

    def testConnectivy(self):
        logger.info("testConnectivity")
        self.assertTrue(True, "assertTrue")

    def testCase2(self):
        self.assertTrue(True, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")
