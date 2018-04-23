import logging
import logging.handlers
import subprocess

CmdTemplate = "C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe " \
              "\". F:\scriptRepo\infrascripts\perfscripts\perf_vert_scale.ps1; " \
              "connectToVC -vc 'vcsa-02a.corp.local' -username 'administrator@corp.local' -password 'VMware1!'; " \
              "{}; " \
              "disconnectFromVC -vc  'vcsa-02a.corp.local' \" "


def execPSCommand(command):
    logger = getLogger('certTest')
    try:
        output = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True)
        logger.info("PowerShell command output: " + output)
    except subprocess.CalledProcessError as e:
        logger.error("PowerShell Command Error")
        logger.error(e)


def getLogger(name):
    ## xinthose (Jun 22, 2016). How to implement a Global Python Logger?
    ## Retrieved from https://stackoverflow.com/questions/37958568/how-to-implement-a-global-python-logger
    # logger settings
    log_file = "log/testing.log"
    log_file_max_size = 1024 * 1024 * 20  # megabytes
    log_num_backups = 3
    log_format = "%(asctime)s [%(levelname)s]: %(filename)s %(funcName)s():%(lineno)s >> %(message)s"
    log_date_format = "%m/%d/%Y %I:%M:%S %p"
    log_filemode = "w"  # w: overwrite; a: append

    # setup logger
    # datefmt=log_date_format
    logging.basicConfig(filename=log_file, format=log_format, filemode=log_filemode, level=logging.DEBUG)
    rotate_file = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=log_file_max_size, backupCount=log_num_backups
    )
    logger = logging.getLogger(name)
    logger.addHandler(rotate_file)

    # print log messages to console
    consoleHandler = logging.StreamHandler()
    logFormatter = logging.Formatter(log_format)
    consoleHandler.setFormatter(logFormatter)
    if (logger.hasHandlers()):
        logger.handlers.clear()

    logger.addHandler(consoleHandler)

    return logger
