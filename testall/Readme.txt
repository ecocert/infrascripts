VMware vApp Certification Automation

How to run:

    1.  Make a directory and clone the repo @ https://github.com/ecocert/infrascripts.git
        in your lab environment.

    2.  Go to the subdirectory “testall”.

    3.  Run the script certTestAll.py
        3.1 To run all tests, simply invoke the script like this:
            shell> .\certTestAll.py

        3.2 To stop on the 1st test failure, please add the option '-f':
            shell> .\certTestAll.py -f

        3.3 To run one particular test case, please specify it in the format as follows:
            shell> .\certTestAll.py TestClassName.ClassMethod

            An example usage is as follows:
            shell> .\certTestAll.py PerformanceTest.testCase1

        3.4 To compose testsuite in command line, please add '-p' for Performance, '-v' for vertical,
            '-h' for horizontal and '-c' for callback

            For example, the following command will run vertical and horizontal tests:
            shell> .\certTestAll.py -v -h