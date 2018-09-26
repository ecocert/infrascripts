#!/usr/bin/env python3
import signal
import time
from performanceTest import *
from verticalScaleTest import *
from horizontalScaleTest import *
from callbackScaleTest import *
from certConfig import *
from util import *

logger = util.getLogger('certTest')


def keyboardInterruptHandler(signalnum, frame):
    "Handle Ctrl+C/SIGINT signal "
    logger.info("keyboardInterruptHandler")
    ## Resource.undeploy()
    raise KeyboardInterrupt


def buildTestList():
    """
    Construt testSet from command line
    Add key/value pair in testDict manually for each test in Certification
    """
    testDict = {
        '-p': PerformanceTest,
        '-v': VerticalScaleTest,
        '-h': HorizontalScaleTest,
        '-c': CallbackScaleTest
    }
    testList = []
    for v in sys.argv:
        if v in testDict.keys():
            testList.append(testDict[v])

    if len(testList) == 0:
        for v in testDict.values():
            testList.append(v)

    return testList


def main():
    # Add CTRL+C handler.  It is experiential feature
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    util.preProcessScript()

    testList = buildTestList()
    testSuite = unittest.TestSuite()
    logger.info(testList)

    for t in testList:
        testSuite.addTest(unittest.makeSuite(t))

    # Stop on the 1st test case failure
    if '-f' in sys.argv:
        runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    # Run over all test cases
    elif len(sys.argv) == 1:
        runner = unittest.TextTestRunner(verbosity=2)
    # Run only on a test case specified by user
    elif sys.argv[1].find('.') != -1:
        logger.info(sys.argv[1].find('.'))
        logger.info(sys.argv[1])
        testClass, test_method = sys.argv[1].split('.')
        testSuite = unittest.TestSuite(map(eval(testClass), [test_method]))
        # test_suite = unittest.TestLoader().loadTestsFromName(PerformanceTest.test_case_1)
        runner = unittest.TextTestRunner(verbosity=2)
    else:
        runner = unittest.TextTestRunner(verbosity=2)

    runner.run(testSuite)


if __name__ == "__main__":
    start = time.time()
    main()
    print("Elapsed time: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start)))
