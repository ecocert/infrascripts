import sys
import unittest
import util

from performanceTest import *
from verticalScaleTest import *
from certConfig import *
from util import *

logger = util.getLogger('certTest')
"""
def certExceptHook(type, value, traceback):
    logger.info("certExecptHook:", type, value, traceback)
sys.excepthook = certExceptHook
"""

def main():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(PerformanceTest))
    test_suite.addTest(unittest.makeSuite(VerticalScaleTest))

    if '-f' in sys.argv:
        ## Stop on the 1st test case failure
        runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    elif len(sys.argv) == 1:
        ## Run over all test cases
        runner = unittest.TextTestRunner(verbosity=2)
    else:
        ## Run only on a test case specified by user
        logger.info(sys.argv[1])
        test_class, test_method = sys.argv[1].split('.')
        test_suite = unittest.TestSuite(map(eval(test_class), [test_method]))
        # test_suite = unittest.TestLoader().loadTestsFromName(PerformanceTest.test_case_1)
        runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


if __name__ == "__main__":
    main()


