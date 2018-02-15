#
# NSX-Callback-Scale-Config-Services
# Description: Callback Scale Config Config Settings
# Author: Satya Dillikar <sdillikar@vmware.com>
# Version: 1.0
# Date: 08/FEB/2018
#
NSX_URL = "https://192.168.10.91/"
USERNAME = "admin"
PASSWORD = "VMware1!"
INPUT_PATH = ".\input\\"
OUTPUT_PATH = ".\output\\"
CB_LOG_FILE = "cb_script.log"
CB_SP_CREATION_TIME_FILE = "sp_creation_time.csv"
CB_SP_APPLY_TIME_FILE = "sp_apply_time.csv"
# keep _COUNT_TOTAL as multiple of GVMs (currently GVMS=4)
SCALE_COUNT_TOTAL = 24

#ip set inputs
GVM_IP_ADDR_FNAME = "gvm_ip_addresses.txt"
IPSET_IN_JSON_FILENAME = "ipset_in.json"
IPSET_OUT_JSON_FILENAME = "ipset_out.json"
IPSET_OUT_OBJECTID_FILENAME = "ipset_obj_ids_out.txt"
IPSET_COUNT_START = 2001
IPSET_NAME_PREFIX = "IpSet_"

#security groups inputs
SG_NAME_PREFIX = "Security_Group_"
SG_COUNT_START = 5001
SG_IN_JSON_FILENAME = "SampleSG_All.json"
SG_OUT_JSON_FILENAME = "sg_out.json"
SG_OUT_OBJECTID_FILENAME = "sg_obj_ids_out.txt"


#security policy inputs
SP_NAME_PREFIX = "Security_Policy_"
SP_COUNT_START = 9001
SP_IN_JSON_FILENAME = "SampleSP_All.json"
SP_OUT_JSON_FILENAME = "sp_out.json"
SP_OUT_OBJECTID_FILENAME = "sp_obj_ids_out.txt"
SP_PRECEDENCE_START = 5000