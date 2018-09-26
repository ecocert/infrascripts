import logging
import logging.handlers
import subprocess
import paramiko

# from paramiko import client


CmdTemplate = "C:/WINDOWS/system32/WindowsPowerShell/v1.0/powershell.exe " \
              "\". F:/scriptRepo/infrascripts/testall/perf_vert_scale.ps1; " \
              "connectToVC -vc 'vcsa-02a.corp.local' -username 'administrator@corp.local' -password 'VMware1!'; " \
              "{}; " \
              "disconnectFromVC -vc  'vcsa-02a.corp.local' \" "


def execPSCommand(command):
    logger.info(command)
    #return

    try:
        output = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True)
        if output.find(" char:") != -1:
            raise Exception("PowerShell command exit status error: " + output)
        logger.info("PowerShell command output: " + output)
    except subprocess.CalledProcessError as e:
        logger.error("PowerShell Command Error")
        logger.error(e)
        raise


def getLogger(name):
    # xinthose (Jun 22, 2016). How to implement a Global Python Logger?
    # Retrieved from https://stackoverflow.com/questions/37958568/how-to-implement-a-global-python-logger
    # logger settings
    log_file = "log/testing.log"
    log_file_max_size = 1024 * 1024 * 20  # megabytes
    log_num_backups = 3
    log_format = "%(asctime)s [%(levelname)s]: %(filename)s %(funcName)s():%(lineno)s >> %(message)s"
    log_date_format = "%m/%d/%Y %I:%M:%S %p"
    log_filemode = "w"  # w: overwrite; a: append

    # setup logger
    # datefmt=log_date_format
    logging.basicConfig(filename=log_file, format=log_format, filemode=log_filemode, level=logging.INFO)
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


class ssh:
    # Daan Lenaets (01/02/2016) Python and SSH: sending commands over SSH using Paramiko
    # Retrieved from: https://daanlenaerts.com/blog/2016/01/02/python-and-ssh-sending-commands-over-ssh-using-paramiko/
    client = None

    def __init__(self, address, username, password):
        logger.info("Connecting to server.")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)

    def sendCommand(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata
                    return str(alldata, "utf8")
        else:
            logger.error("Connection not opened.")


class Server():
    # implement scp/sftp on Windows
    # Ryan Ginstrom, 2009,  Easy SFTP uploading with paramiko
    # Retrieved from: http://ginstrom.com/scribbles/2009/09/14/easy-sftp-uploading-with-paramiko/
    def __init__(self, username, password, host, port=22):
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def upload(self, local, remote):
        self.sftp.put(local, remote)

    def download(self, remote, local):
        self.sftp.get(remote, local)

    def close(self):
        """
        Close the connection if it's active
        """

        if self.transport.is_active():
            self.sftp.close()
            self.transport.close()

    # with-statement support
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()


#
# Remove the last 3 lines in the PowerShell script,
# because they are the code to start the script.
#
"""
def preProcessScript(filename="../perfscripts/perf_vert_scale.ps1"):
    with open(filename, "r") as fr:
        content_r = fr.readlines()
        content_w = content_r[:-3]
        with open("./perf_vert_scale.ps1", "w") as fw:
            fw.write("".join(content_w))
"""


#
# Tail dispatcher.log via ssh
#
def tail_dispatcher():
    logger.info("tail -f dispatcher.log")
    ssh_client = ssh("10.148.254.1", "certadmin", "VMware1!")
    while True:
        ret = ssh_client.sendCommand("tailf /home/certadmin/Dispatccher/dispatcher.log")
        if ret.find("CANCEL") != -1:
            logger.error(ret)


logger = getLogger('certTest')
