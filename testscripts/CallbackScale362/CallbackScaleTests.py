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

import requests    #library used for making REST API calls
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def menu():
    c = CallbackScale()
    while(True):
        print("1. CB Scale Config Setup")
        print("2. CB Scale Config Cleanup")

        print("11. IpSet Query")
        print("12. IpSet Create")
        print("13. IpSet Delete")

        print("14. Security Group Query")
        print("15. Security Group Create")
        print("16. Security Group Delete")

        print("17. Security Policy Query")
        print("18. Security Policy Create")
        print("19. Security Policy Delete")
        print("20. Apply Security Policies")

        menuid = input("Enter Your Choice:  ")
        jobid = -1
        if(menuid == str(1)):
            gvm_ip_file = constants.INPUT_PATH + constants.GVM_IP_ADDR_FNAME
            cb_scale_count = constants.SCALE_COUNT_TOTAL
            jobid = c.cb_scale_config_setup(gvm_ip_file, cb_scale_count)
        elif (menuid == str(2)):
            jobid = c.cb_scale_config_cleanup()
            #delete object
            #del c
        elif(menuid == str(11)):
            jobid = c.cb_scale_ipset_query()
        elif (menuid == str(12)):
            gvm_ip_file = constants.INPUT_PATH + constants.GVM_IP_ADDR_FNAME
            jobid = c.cb_scale_ipset_create(gvm_ip_file)
        elif (menuid == str(13)):
            jobid = c.cb_scale_ipset_delete()
        elif (menuid == str(14)):
            jobid = c.cb_scale_sec_group_query()
        elif (menuid == str(15)):
            jobid = c.cb_scale_sec_group_create(constants.SCALE_COUNT_TOTAL)
        elif (menuid == str(16)):
            jobid = c.cb_scale_sec_group_delete()
        elif (menuid == str(17)):
            jobid = c.cb_scale_sec_policy_query()
        elif (menuid == str(18)):
            jobid = c.cb_scale_sec_policy_create()
        elif (menuid == str(19)):
            jobid = c.cb_scale_sec_policy_delete()
        elif (menuid == str(20)):
            jobid = c.cb_scale_sec_policy_apply()
        else:
            print (" -------------------")
            print("invalid choice try again \n")
        if(jobid != -1):
            print("jobID is {0}".format(jobid))

if __name__ == '__main__':
    menu()
