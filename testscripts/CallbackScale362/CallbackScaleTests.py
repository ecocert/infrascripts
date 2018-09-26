#!/usr/bin/python
#
# NSX-Callback-Scale-Config-Services
# Description: Callback Scale Config Setup and Cleanup Trigger Script
# Author: Satya Dillikar <sdillikar@vmware.com>
# Version: 1.0
# Date: 08/FEB/2018
#
from CallbackScaleUtils import CallbackScale
import constants
import os

import requests    #library used for making REST API calls
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def menu():
    c = CallbackScale()
    while(True):
        print("1. CB Scale Config Setup")
        print("2. CB Scale Config Cleanup")
        menuid = input("Enter Your Choice:  ")
        rc = False
        if(menuid == str(1)):
            in_fname = constants.INPUT_PATH + constants.GVM_INPUT_FNAME
            if not os.path.isfile(in_fname):
                print("WARN : FILE DOES NOT EXISTS " + in_fname)
                return False
            cb_scale_count = constants.SCALE_COUNT_TOTAL
            rc = c.cb_scale_config_setup(in_fname, cb_scale_count)
        elif (menuid == str(2)):
            rc = c.cb_scale_config_cleanup()
        elif (menuid == str(3)):
            rc = c.cb_scale_sec_policy_create_xml()
        else:
            print (" -------------------")
            print("invalid choice try again \n")
        if(rc == False):
            print("rc is False")

if __name__ == '__main__':
    menu()
