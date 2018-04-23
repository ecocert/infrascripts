import sys
import unittest
import util

from performanceTest import *
from verticalScaleTest import *

logger = util.getLogger('certTest')

if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(PerformanceTest))
    test_suite.addTest(unittest.makeSuite(VerticalScaleTest))

    if '-f' in sys.argv:
        runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    elif len(sys.argv) == 1:
        runner = unittest.TextTestRunner(verbosity=2)
    else:
        logger.info(sys.argv[1])
        test_class, test_method = sys.argv[1].split('.')
        test_suite = unittest.TestSuite(map(eval(test_class), [test_method]))
        # test_suite = unittest.TestLoader().loadTestsFromName(PerformanceTest.test_case_1)
        runner = unittest.TextTestRunner(verbosity=2)

    runner.run(test_suite)
