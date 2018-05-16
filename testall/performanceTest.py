#!/usr/bin/env python3

import unittest
import util
import subprocess
from certConfig import Resource
import time

logger = util.getLogger('certTest')


class PerformanceTest(unittest.TestCase):
    res = Resource("PerformanceTest")

    @classmethod
    def setUpClass(cls):
        try:
            logger.info("---------------------------------------")
            logger.info("set up the fixture for Performance Test")
            cls.res.preTestValidation()
            cls.res.configure()
            cls.res.deployIxia()
            time.sleep(15)
            cls.res.deployInfrastucture()
            cls.res.powerOnIXIA()
            logger.info("Press ENTER to continue...")
            input()
        except:
            cls.res.cleaner.pop_all().close()
            cls.res.saveLog()
            raise

    @classmethod
    def tearDownClass(cls):
        logger.info("tear down the fixture for Performance Test")
        # unwind all using ExitStatck
        cls.res.undeployAll()
        cls.res.saveLog()

    def test_loadQuickTest(self):
        self.assertTrue(True, "assertTrue")
        command = "F:\\programs\\python.exe " \
                  "C:/Users/Administrator/PycharmProjects/performance/loadQuickTestRestApi.py " \
                  "windowsConnectionMgr"
        try:
            output = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                shell=True,
                universal_newlines=True,
                timeout=60
            )
            logger.info("command output: " + output)

        except subprocess.CalledProcessError as e:
            logger.error(e)

    def testCase2(self):
        self.assertTrue(False, "assertFalse")

    def testCase3(self):
        self.assertTrue(True, "assertTrue")
