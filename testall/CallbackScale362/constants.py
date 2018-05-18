#
# NSX-Callback-Scale-Config-Services
# Description: Callback Scale Config Config Settings
# Author: Satya Dillikar <sdillikar@vmware.com>
# Version: 1.0
# Date: 08/FEB/2018
#
NSX_URL = "https://172.17.11.11/"
USERNAME = "admin"
PASSWORD = "VMware1!"
INPUT_PATH = "./input/"
OUTPUT_PATH = "./output/"
CB_LOG_FILE = "cb_script.log"
CB_SP_CREATION_TIME_FILE = "sp_creation_time.csv"
CB_SP_APPLY_TIME_FILE = "sp_apply_time.csv"
SCALE_COUNT_TOTAL = 10
# Set SG_BINDING_COUNT less than 128
SG_BINDING_COUNT = 3
NUM_RETRIES = 3
WAIT_IN_SEC = (100.0 / 1000.0)

GVM_INPUT_FNAME = "gvm_object_ids.txt"

# security groups inputs
SG_NAME_PREFIX = "Security_Group_"
SG_COUNT_START = 5001
SG_IN_JSON_FILENAME = "SampleSG_All.json"

# security policy inputs
SP_NAME_PREFIX = "Security_Policy_"
SP_COUNT_START = 9001
SP_PRECEDENCE_START = 5000
SP_POLICY_PAYLOAD_NI_FILENAME = "se_policy_payload_ni.xml"

#
# Set the value from json
#
# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
import certConfig
config = certConfig.CertJsonConfig()
cfg = config.json["CallbackScaleTest"]
NSX_URL = cfg["NSX_URL"]
USERNAME = cfg["USERNAME"]
PASSWORD = cfg["PASSWORD"]
INPUT_PATH = cfg["INPUT_PATH"]
OUTPUT_PATH = cfg["OUTPUT_PATH"]
CB_LOG_FILE = cfg["CB_LOG_FILE"]
CB_SP_CREATION_TIME_FILE = cfg["CB_SP_CREATION_TIME_FILE"]
CB_SP_APPLY_TIME_FILE = cfg["CB_SP_APPLY_TIME_FILE"]
SCALE_COUNT_TOTAL = cfg["SCALE_COUNT_TOTAL"]
SG_BINDING_COUNT = cfg["SG_BINDING_COUNT"]
NUM_RETRIES = cfg["NUM_RETRIES"]
WAIT_IN_SEC = cfg["WAIT_IN_SEC"]
GVM_INPUT_FNAME = cfg["GVM_INPUT_FNAME"]
SG_NAME_PREFIX = cfg["SG_NAME_PREFIX"]
SG_COUNT_START = cfg["SG_COUNT_START"]
SG_IN_JSON_FILENAME = cfg["SG_IN_JSON_FILENAME"]
SP_NAME_PREFIX = cfg["SP_NAME_PREFIX"]
SP_COUNT_START = cfg["SP_COUNT_START"]
SP_PRECEDENCE_START = cfg["SP_PRECEDENCE_START"]
SP_POLICY_PAYLOAD_NI_FILENAME = cfg["SP_POLICY_PAYLOAD_NI_FILENAME"]
"""
