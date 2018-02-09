#!/usr/bin/python
#
# NSX-Callback-Scale-Config-Services
# Description: Callback Scale Config Utilities for create/delete/query
# for IP-Set,Security-Groups & Security-Policies
# Author: Satya Dillikar <sdillikar@vmware.com>
# Version: 1.0
# Date: 08/FEB/2018
#
import constants
import requests    #library used for making REST API calls
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import time
import os
#from itertools import izip
import io
import logging

myheaders={'content-type':'application/json', 'accept':'application/json'}

class CallbackScale:

    def __init__(self):
        self.username = constants.USERNAME
        self.password = constants.PASSWORD

        logfile = constants.OUTPUT_PATH + constants.CB_LOG_FILE
        try:
            os.remove(logfile)
        except OSError:
            pass
        '''
        logging.basicConfig(filename=logfile,
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d:%(funcName)-15s ] %(message)s',
                            datefmt='%d-%m-%Y:%H:%M:%S',
                            level=logging.DEBUG)
        '''
        logging.basicConfig(filename=logfile,
                            format='%(asctime)-s,%(msecs)-5d %(levelname)-8s [%(filename)-s:%(lineno)-4d:%(funcName)-s] %(message)s',
                            datefmt='%d-%m-%Y:%H:%M:%S',
                            level=logging.INFO)
        '''

        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)  # or whatever
        handler = logging.FileHandler(logfile, 'w', encoding="UTF-8")  # or whatever
        formatter = logging.Formatter('%(asctime)-s,%(msecs)-5d %(levelname)-8s [%(filename)-s:%(lineno)-4d] %(message)s')  # or whatever
        handler.setFormatter(formatter)  # Pass handler as a parameter, not assign
        self.root_logger.addHandler(handler)
        logging.debug('entered constructor')
        '''

    def __del__(self):
        print ("destructor")
        logging.info('entered destructor')

    def cb_scale_ipset_create(self, filename):
        logging.debug("ENTER")
        count = 0
        api_path = '/api/2.0/services/ipset/globalroot-0'
        nsx_url = constants.NSX_URL + api_path
        ipset_input_fname = constants.INPUT_PATH+constants.IPSET_IN_JSON_FILENAME

        with open(ipset_input_fname) as datafile:
             jdata = json.load(datafile)

        ipset_obj_output_fname = constants.OUTPUT_PATH+constants.IPSET_OUT_OBJECTID_FILENAME

        if os.path.isfile(ipset_obj_output_fname):
            print("WARN : FILE EXISTS " + ipset_obj_output_fname)
            print("IPSETS might be already create. Hence returning.")
            return False

        outfile = open(ipset_obj_output_fname, "w")

        with open(filename) as ipfile:
            for ip in ipfile:
                ip = ip.rstrip()
                if ip:
                    name = constants.IPSET_NAME_PREFIX+ str(constants.IPSET_COUNT_START + count)
                    count += 1
                    #time.sleep(50.0/1000.0)
                    jdata['name'] = name
                    jdata['value'] = ip
                    #print "["+ip+"]"
                    try:
                        response = requests.post(nsx_url, json=jdata, headers=myheaders,
                                                 auth=(constants.USERNAME, constants.PASSWORD), verify=False)
                    except requests.exceptions.ConnectionError as e:
                        print("Connection error!")

                    if (response.status_code == 201):
                        ipset_obj_id = response.text
                        #print "CREATED IPSET " + name + " object-id = " + ipset_obj_id
                        logging.info("CREATED IPSET " + name + " object-id = " + ipset_obj_id)
                        outfile.write(ipset_obj_id)
                        outfile.write("\n")
                    else:
                        #print "ERROR: CREATING IPSET " + name + " status code = " + str(response.status_code)
                        logging.error("CREATING IPSET " + name + " status code = " + str(response.status_code))

        datafile.close()
        outfile.close()
        logging.debug("EXIT")

        return True

    def cb_scale_ipset_delete(self):
        logging.debug("ENTER")

        api_path = '/api/2.0/services/ipset/'
        nsx_url = constants.NSX_URL + api_path

        ipset_obj_output_fname = constants.OUTPUT_PATH+constants.IPSET_OUT_OBJECTID_FILENAME

        if not os.path.isfile(ipset_obj_output_fname):
            print("WARN : FILE DOES NOT EXISTS "+ipset_obj_output_fname)
            print("IPSETS might be already deleted. Hence returning.")
            return True

        with open(ipset_obj_output_fname, "r") as outfile:
            for line in outfile:
                ipset_obj_id = line.strip()
                #time.sleep(50.0 / 1000.0)

                myurl = nsx_url + ipset_obj_id.__str__() + '?force=false'
                try:
                    response = requests.delete(myurl, headers=myheaders,
                                             auth=(constants.USERNAME,constants.PASSWORD), verify=False)
                except requests.exceptions.ConnectionError as e:
                    print ("Connection error!")
                if (response.status_code == 200):
                    #print "DELETED IPSET "+ ipset_obj_id
                    logging.info("DELETED IPSET "+ ipset_obj_id)
                else:
                    #print "ERROR: DELETING IPSET "+ipset_obj_id + " status code = " + str(response.status_code)
                    logging.error("DELETING IPSET "+ipset_obj_id + " status code = " + str(response.status_code))

        outfile.close()

        try:
            os.remove(ipset_obj_output_fname)
        except OSError:
            pass

        logging.debug("EXIT")
        return True


    def cb_scale_ipset_query(self):
        #print("cb_scale_ipset_query")
        logging.debug("ENTER")

        api_path = '/api/2.0/services/ipset/scope/globalroot-0'
        nsx_url = constants.NSX_URL + api_path
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print("Connection error!")

        data = response.json()
        #print data
        ipset_output_fname = constants.OUTPUT_PATH+constants.IPSET_OUT_JSON_FILENAME
        #print ipset_output_fname
        with open(ipset_output_fname, "w") as outfile:
            json.dump(data, outfile, indent=4)

        outfile.close()
        logging.debug("EXIT")

        return True

    def cb_scale_sec_group_create(self, scale_count):
        #print("cb_scale_sec_group_create")
        api_path = 'api/2.0/services/securitygroup/bulk/globalroot-0'
        nsx_url = constants.NSX_URL + api_path

        onesg_filename = constants.INPUT_PATH + constants.SG_IN_JSON_FILENAME
        with open(onesg_filename) as datafile:
            jdata = json.load(datafile)
            segroup = jdata[0]

        datafile.close()

        ipset_obj_output_fname = constants.OUTPUT_PATH+constants.IPSET_OUT_OBJECTID_FILENAME

        if not os.path.isfile(ipset_obj_output_fname):
            print("WARN : FILE DOES NOT EXISTS "+ipset_obj_output_fname)
            print ("IPSETS might be already deleted. Hence returning.")
            return False

        sg_obj_output_fname = constants.OUTPUT_PATH+constants.SG_OUT_OBJECTID_FILENAME

        if os.path.isfile(sg_obj_output_fname):
            print ("ERROR : FILE EXISTS "+sg_obj_output_fname)
            print ("SG OBJECT-IDs might be already created. Hence returning.")
            return False

        outfile = open(sg_obj_output_fname, "w")

        ipset_obj_list = []
        with open(ipset_obj_output_fname) as ipset_obj_fd:
            ipset_obj_list = ipset_obj_fd.read().splitlines()
            ipset_obj_fd.close()

        sg_count = 0
        sg_success_cnt = 0
        sg_fail_cnt = 0
        while (sg_count < scale_count) :
            for ipset_id in ipset_obj_list:
                #time.sleep(100.0 / 1000.0)
                segroup['name'] = constants.SG_NAME_PREFIX + str(constants.SG_COUNT_START + sg_count)
                ipset_id = ipset_id.strip()
                sg_count += 1
                segroup['members'][0]['objectId'] = ipset_id
                payload = segroup

                try:
                    response = requests.post(nsx_url, json=payload, headers=myheaders,
                                             auth=(constants.USERNAME, constants.PASSWORD), verify=False)
                except requests.exceptions.ConnectionError as e:
                    print("Connection error!")

                if (response.status_code == 201):
                    sg_obj_id = response.text
                    #print("SG-["+sg_obj_id+"]")
                    outfile.write(sg_obj_id)
                    outfile.write("\n")
                    sg_success_cnt +=1
                    #print "CREATED SG " + segroup['name']  + " object-id = " + sg_obj_id
                    logging.info("CREATED SG " + segroup['name']  + " object-id = " + sg_obj_id)
                else:
                    #print "ERROR: CREATING SG " + segroup['name']  + " status code = " + str(response.status_code)
                    logging.error("CREATING SG " + segroup['name']  + " status code = " + str(response.status_code))
                    sg_fail_cnt +=1

        print("SG CREATION : success_count=" + str(sg_success_cnt) + " failure_count="+ str(sg_fail_cnt))
        logging.info("SG CREATION : success_count=" + str(sg_success_cnt) + " failure_count="+ str(sg_fail_cnt))

        outfile.close()
        logging.debug("EXIT")

        return True

    def cb_scale_sec_group_delete(self):
        logging.debug("ENTER")

        api_path = 'api/2.0/services/securitygroup/'
        nsx_url = constants.NSX_URL + api_path

        sg_obj_output_fname = constants.OUTPUT_PATH+constants.SG_OUT_OBJECTID_FILENAME
        if not os.path.isfile(sg_obj_output_fname):
            print ("WARN : FILE DOES NOT EXISTS "+sg_obj_output_fname)
            print ("SGs might be already deleted. Hence returning.")
            # nothing to do, just continue hence return True
            return True

        with open(sg_obj_output_fname, "r") as outfile:
            for line in outfile:
                sg_obj_id = line.strip()
                #time.sleep(100.0 / 1000.0)

                myurl = nsx_url + sg_obj_id.__str__() + '?force=false'
                try:
                    response = requests.delete(myurl, headers=myheaders,
                                             auth=(constants.USERNAME,constants.PASSWORD), verify=False)
                except requests.exceptions.ConnectionError as e:
                    print ("Connection error!")
                if (response.status_code == 200):
                    #print "DELETED SG " + sg_obj_id
                    logging.info("DELETED SG " + sg_obj_id)
                else:
                    #print "ERROR: DELETING SG " + sg_obj_id + " status code = "+ response.status_code
                    logging("DELETING SG " + sg_obj_id + " status code = "+ str(response.status_code))

        outfile.close()

        try:
            os.remove(sg_obj_output_fname)
        except OSError:
            pass
        logging.debug("EXIT")
        return True

    def cb_scale_sec_group_query(self):
        logging.debug("ENTER")

        api_path = '/api/2.0/services/securitygroup/scope/globalroot-0'
        nsx_url = constants.NSX_URL + api_path
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")

        data = response.json()
        segroup_output_fname = constants.OUTPUT_PATH+constants.SG_OUT_JSON_FILENAME
        with open(segroup_output_fname, "w") as outfile:
            json.dump(data, outfile, indent=4)

        outfile.close()
        logging.debug("EXIT")

        return True


    def cb_scale_sec_policy_create(self):
        logging.debug("ENTER")

        api_path = 'api/2.0/services/policy/securitypolicy'
        nsx_url = constants.NSX_URL + api_path
        sp_count = constants.SP_COUNT_START
        onesp_filename = constants.INPUT_PATH + constants.SP_IN_JSON_FILENAME
        with open(onesp_filename) as datafile:
            jdata = json.load(datafile)
            #TODO : replay this for all sp policy file
            sepolicy = jdata['policies'][0]
            #sepolicy = jdata
        datafile.close()
        #print sepolicy
        #print sepolicy['name']

        sg_obj_output_fname = constants.OUTPUT_PATH+constants.SG_OUT_OBJECTID_FILENAME
        if not os.path.isfile(sg_obj_output_fname):
            print ("WARN : FILE DOES NOT EXISTS "+sg_obj_output_fname)
            print ("SGs might be already deleted. Hence returning.")
            return False


        sp_obj_output_fname = constants.OUTPUT_PATH+constants.SP_OUT_OBJECTID_FILENAME
        sp_create_time_fname = constants.OUTPUT_PATH + constants.CB_SP_CREATION_TIME_FILE

        '''
        # TODO: remove after testing
        try:
            os.remove(sp_obj_output_fname)
        except OSError:
            pass
        '''

        if os.path.isfile(sp_obj_output_fname):
            print ("WARN : FILE EXISTS "+sp_obj_output_fname)
            print ("SP OBJECT-IDs might be already created. Hence returning.")
            return False

        outfile = open(sp_obj_output_fname, "w")
        timefile = open(sp_create_time_fname, "w")
        sp_success_cnt = 0
        sp_fail_cnt = 0
        sp_count = 0
        total_elapsed_time = 0
        with open(sg_obj_output_fname) as sg_obj_fd:
            for sg_id in sg_obj_fd:
                #time.sleep(50.0 / 1000.0)
                sepolicy_name = constants.SP_NAME_PREFIX + str(constants.SP_COUNT_START + sp_count)
                sg_id = sg_id.strip()
                sp_count += 1
                sepolicy['name'] = sepolicy_name
                sepolicy['precedence'] = constants.SP_PRECEDENCE_START+sp_count
                #sepolicy['auditableMap']['precedence'] = constants.SP_PRECEDENCE_START+sp_count

                #sepolicy['policies'][0]['members'][0]['objectId'] = sg_id
                payload = sepolicy
                #print payload
                start = time.clock()
                try:
                    response = requests.post(nsx_url, json=payload, headers=myheaders,
                                             auth=(constants.USERNAME, constants.PASSWORD), verify=False)
                except requests.exceptions.ConnectionError as e:
                    print ("Connection error!")
                end = time.clock()
                elapsed_time = end - start
                timefile.write(str(sp_count) + ',' + str(elapsed_time) + '\n')
                total_elapsed_time += elapsed_time

                if (response.status_code == 201):
                    sp_obj_id = response.text
                    outfile.write(sp_obj_id)
                    outfile.write("\n")
                    sp_success_cnt +=1
                    #print "CREATED SP " + sepolicy_name + " object-id = " + sp_obj_id
                    logging.info("CREATED SP " + sepolicy_name + " object-id = " + sp_obj_id)
                else:
                    #print "ERROR: CREATING SP " + sepolicy_name  + " status code = " + str(response.status_code)
                    logging.error("CREATING SP " + sepolicy_name  + " status code = " + str(response.status_code))
                    sp_fail_cnt +=1

        print ("SP CREATION : success_count=" + str(sp_success_cnt) + " failure_count="+ str(sp_fail_cnt))
        print ("TOTAL SP CREATION time is : " + str(total_elapsed_time) + " seconds ...")
        logging.info("SP CREATION : success_count=" + str(sp_success_cnt) + " failure_count="+ str(sp_fail_cnt))
        logging.info("TOTAL SP CREATION time is : " + str(total_elapsed_time) + " seconds ...")

        outfile.close()
        timefile.close()
        sg_obj_fd.close()

        logging.debug("EXIT")
        return True


    def cb_scale_sec_policy_delete(self):
        logging.debug("ENTER")

        api_path = 'api/2.0/services/policy/securitypolicy/'
        nsx_url = constants.NSX_URL + api_path

        sp_obj_output_fname = constants.OUTPUT_PATH+constants.SP_OUT_OBJECTID_FILENAME
        if not os.path.isfile(sp_obj_output_fname):
            print ("WARN : FILE DOES NOT EXISTS "+sp_obj_output_fname)
            print ("SPs might be already deleted. Hence returning.")
            # nothing to do, just continue hence return True
            return True

        with open(sp_obj_output_fname, "r") as outfile:
            for line in outfile:
                sp_obj_id = line.strip()
                #time.sleep(50.0 / 1000.0)

                myurl = nsx_url + sp_obj_id.__str__() + '?force=false'
                try:
                    response = requests.delete(myurl, headers=myheaders,
                                             auth=(constants.USERNAME,constants.PASSWORD), verify=False)
                except requests.exceptions.ConnectionError as e:
                    print ("Connection error!")
                if (response.status_code == 200 or response.status_code == 204):
                    #print "DELETED SP " + sp_obj_id
                    logging.info("DELETED SP " + sp_obj_id)
                else:
                    #print "ERROR: DELETING SP " + sp_obj_id + " status code = "+ str(response.status_code)
                    logging.error("DELETING SP " + sp_obj_id + " status code = "+ str(response.status_code))

        outfile.close()
        try:
            os.remove(sp_obj_output_fname)
        except OSError:
            pass

        logging.debug("EXIT")
        return True


    def cb_scale_sec_policy_query(self):
        logging.debug("ENTER")

        api_path = 'api/2.0/services/policy/securitypolicy/all'
        #api_path = 'api/2.0/services/policy/securitypolicy/policy-74'

        nsx_url = constants.NSX_URL + api_path
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")

        data = response.json()
        sp_output_fname = constants.OUTPUT_PATH+constants.SP_OUT_JSON_FILENAME
        with open(sp_output_fname, "w") as outfile:
            json.dump(data, outfile, indent=4)

        outfile.close()
        logging.debug("EXIT")

        return True

    def cb_scale_sec_policy_apply(self):
        logging.debug("ENTER")

        #PUT /api/2.0/services/policy/securitypolicy/{ID}/sgbinding/{securityGroupId}

        api_path = 'api/2.0/services/policy/securitypolicy/'
        nsx_url = constants.NSX_URL + api_path

        sp_apply_time_fname = constants.OUTPUT_PATH + constants.CB_SP_APPLY_TIME_FILE
        sp_obj_output_fname = constants.OUTPUT_PATH + constants.SP_OUT_OBJECTID_FILENAME

        if not os.path.isfile(sp_obj_output_fname):
            print ("ERROR : FILE DOES NOT EXISTS " + sp_obj_output_fname)
            print ("SPs might be already deleted. Hence returning.")
            # nothing to do, just continue hence return True
            return True

        sg_obj_output_fname = constants.OUTPUT_PATH+constants.SG_OUT_OBJECTID_FILENAME

        if not os.path.isfile(sg_obj_output_fname):
            print ("ERROR : FILE DOES NOT EXISTS "+sg_obj_output_fname)
            print ("SGs might be already deleted. Hence returning.")
            # nothing to do, just continue hence return True
            return True

        sg_outfile = open(sg_obj_output_fname)
        sp_outfile = open(sp_obj_output_fname)
        timefile = open(sp_apply_time_fname, "w")
        total_elapsed_time = 0
        sp_count = 0
        #for sg_line, sp_line in izip(sg_outfile, sp_outfile):
        for sg_line, sp_line in zip(sg_outfile, sp_outfile):
            sg_obj_id = sg_line.rstrip()
            sp_obj_id = sp_line.rstrip()
            #print "%s\t%s" % (sg_obj_id, sp_obj_id)
            #time.sleep(50.0 / 1000.0)
            sp_count += 1
            myurl = nsx_url + sp_obj_id.__str__() + '/sgbinding/' + sg_obj_id.__str__()
            #print myurl
            start = time.clock()
            try:
                response = requests.put(myurl, headers=myheaders,
                                           auth=(constants.USERNAME, constants.PASSWORD), verify=False)
            except requests.exceptions.ConnectionError as e:
                print ("Connection error!")
            end = time.clock()
            elapsed_time = end - start
            timefile.write(str(sp_count) + ',' + str(elapsed_time) + '\n')
            total_elapsed_time += elapsed_time
            if (response.status_code == 200 or response.status_code == 204):
                #print "APPLIED SP " + sp_obj_id + " TO " + sg_obj_id
                logging.info("APPLIED SP " + sp_obj_id + " TO " + sg_obj_id)
            else:
                #print "ERROR: APPLYING SP " + sp_obj_id + " status code = " + str(response.status_code)
                logging.error("APPLYING SP " + sp_obj_id + " status code = " + str(response.status_code))

        print ("TOTAL SP APPLY time is : " + str(total_elapsed_time) + " seconds ...")
        logging.info("TOTAL SP APPLY time is : " + str(total_elapsed_time) + " seconds ...")
        timefile.close()
        sg_outfile.close()
        sp_outfile.close()
        logging.debug("EXIT")

        return True

    def cb_scale_config_setup(self, input_fname, scale_count):
        print ("Started Callback Scale Infra Setup...")
        logging.debug("ENTER")

        ret = self.cb_scale_ipset_create(input_fname)
        if ret != True:
            print ("ERROR: IPSET Create")

        ret = self.cb_scale_sec_group_create(scale_count)
        if ret != True:
            print ("ERROR: SE Group Create")

        ret = self.cb_scale_sec_policy_create()
        if ret != True:
            print ("ERROR: SE Policy Create")

        ret = self.cb_scale_sec_policy_apply()
        if ret != True:
            print ("ERROR: SE Policy Apply")

        print ("Completed Callback Scale Infra Setup. Done")
        logging.debug("EXIT")

        return True

    def cb_scale_config_cleanup(self):
        print ("Started Callback Scale Infra Cleanup...")
        logging.debug("ENTER")

        ret = self.cb_scale_sec_policy_delete()
        if ret != True:
            print ("ERROR: SE Policy Delete")

        ret = self.cb_scale_sec_group_delete()
        if ret != True:
            print ("ERROR: SE Group Delete")

        ret = self.cb_scale_ipset_delete()
        if ret != True:
            print ("ERROR: IPSET Delete")

        print ("Completed Callback Scale Infra Cleanup. Done")
        logging.debug("EXIT")

        return True