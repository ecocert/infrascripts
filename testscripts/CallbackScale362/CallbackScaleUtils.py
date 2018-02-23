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
import time
import os
import io
import logging
myheaders={'content-type':'application/json', 'accept':'application/json'}

class CallbackScale:

    def __init__(self):
        logfile = constants.OUTPUT_PATH + constants.CB_LOG_FILE
        try:
            os.remove(logfile)
        except OSError:
            pass

        logging.basicConfig(filename=logfile,
                            format='%(asctime)-s,%(msecs)-5d %(levelname)-8s [%(filename)-s:%(lineno)-4d:%(funcName)-s] %(message)s',
                            datefmt='%d-%m-%Y:%H:%M:%S',
                            level=logging.INFO)


    def __del__(self):
        print ("destructor")
        logging.info('entered destructor')


    def cb_scale_sec_group_create(self, in_fname, scale_count):
        api_path = 'api/2.0/services/securitygroup/bulk/globalroot-0'
        nsx_url = constants.NSX_URL + api_path

        onesg_filename = constants.INPUT_PATH + constants.SG_IN_JSON_FILENAME
        with open(onesg_filename) as datafile:
            jdata = json.load(datafile)
            segroup = jdata[0]
        datafile.close()


        obj_list = []
        with open(in_fname) as obj_fd:
            obj_list = obj_fd.read().splitlines()
            obj_fd.close()

        sg_count = 0
        sg_success_cnt = 0
        sg_fail_cnt = 0
        loop_cond = True
        while (loop_cond):
            for id in obj_list:
                if(sg_count >= scale_count):
                    loop_cond = False
                    break
                segroup['name'] = constants.SG_NAME_PREFIX + str(constants.SG_COUNT_START + sg_count)
                id = id.strip()
                sg_count += 1
                segroup['members'][0]['objectId'] = id
                payload = segroup
                time.sleep(constants.WAIT_IN_SEC)
                try:
                    response = requests.post(nsx_url, json=payload, headers=myheaders,
                                             auth=(constants.USERNAME, constants.PASSWORD), verify=False)
                except requests.exceptions.ConnectionError as e:
                    print("Connection error!")

                if (response.status_code == 201):
                    sg_obj_id = response.text
                    #print("SG-["+sg_obj_id+"]")
                    sg_success_cnt +=1
                    #print "CREATED SG " + segroup['name']  + " object-id = " + sg_obj_id
                    logging.info("CREATED SG " + segroup['name']  + " object-id = " + sg_obj_id)
                else:
                    #print "ERROR: CREATING SG " + segroup['name']  + " status code = " + str(response.status_code)
                    logging.error("CREATING SG " + segroup['name']  + " status code = " + str(response.status_code))
                    sg_fail_cnt +=1

        print("SG CREATION : success_count=" + str(sg_success_cnt) + " failure_count="+ str(sg_fail_cnt))
        logging.info("SG CREATION : success_count=" + str(sg_success_cnt) + " failure_count="+ str(sg_fail_cnt))

        logging.debug("EXIT")

        return True

    def cb_scale_sec_group_query_and_delete_all(self):
        logging.debug("ENTER")

        #Query and get all security-groups
        api_path = 'api/2.0/services/securitygroup/scope/globalroot-0'
        nsx_url = constants.NSX_URL + api_path
        #print(nsx_url)
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")

        jdata = response.json()

        #Delete each object
        api_path = 'api/2.0/services/securitygroup/'
        nsx_url = constants.NSX_URL + api_path

        for segroup in jdata:
            sg_name = segroup['name']
            # print(sg_name)
            if (sg_name.startswith(constants.SG_NAME_PREFIX)):
                sg_obj_id = segroup['objectId']
                #print(sg_name + " " + sg_obj_id)
                myurl = nsx_url + sg_obj_id.__str__() + '?force=true'
                #print(myurl)
                try_more = True
                try_count = 0
                while (try_more and try_count <constants.NUM_RETRIES):
                    try_more = False
                    try_count +=1
                    time.sleep(try_count * constants.WAIT_IN_SEC)
                    try:
                        response = requests.delete(myurl, headers=myheaders,
                                                 auth=(constants.USERNAME,constants.PASSWORD), verify=False)
                    except requests.exceptions.ConnectionError as e:
                        print ("Connection error!")
                    if (response.status_code == 200):
                        #print "DELETED SG " + sg_obj_id
                        logging.info("DELETED SG " + sg_obj_id)
                    elif (response.status_code == 500):
                        #print "DELETED SG " + sg_obj_id
                        logging.info("RE-TRY DELETING SG " + sg_obj_id)
                        try_more = True
                    else:
                        #print "ERROR: DELETING SG " + sg_obj_id + " status code = "+ response.status_code
                        logging.error("DELETING SG " + sg_obj_id + " status code = " + str(response.status_code))

        logging.debug("EXIT")
        return True

    def cb_scale_sec_policy_create_xml(self):
        logging.debug("ENTER")

        #query manually created policy
        api_path = 'api/2.0/services/policy/securitypolicy/all'
        nsx_url = constants.NSX_URL + api_path
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")
            return False

        jdata = response.json()
        sepolicy = jdata['policies'][0]

        #create new policies
        api_path = 'api/2.0/services/policy/securitypolicy'
        nsx_url = constants.NSX_URL + api_path
        sp_count = constants.SP_COUNT_START

        serviceprofile_obj_id = sepolicy['auditableMap']['actionsByCategory']['endpoint']['action-1']['serviceProfile']['objectId']
        service_obj_id = sepolicy['auditableMap']['actionsByCategory']['endpoint']['action-1']['serviceId']
        #print ("serviceprofile_obj_id = "+serviceprofile_obj_id)
        #print("service_obj_id ="+service_obj_id)

        sp_create_time_fname = constants.OUTPUT_PATH + constants.CB_SP_CREATION_TIME_FILE

        timefile = open(sp_create_time_fname, "w")
        sp_success_cnt = 0
        sp_fail_cnt = 0
        sp_count = 0
        total_elapsed_time = 0
        while sp_count < constants.SCALE_COUNT_TOTAL :
            #Add delay
            time.sleep(constants.WAIT_IN_SEC)
            sepolicy_name = constants.SP_NAME_PREFIX + str(constants.SP_COUNT_START + sp_count)

            sp_count += 1
            sepolicy['name'] = sepolicy_name
            sepolicy['precedence'] = constants.SP_PRECEDENCE_START+sp_count
            sepolicy_pred = constants.SP_PRECEDENCE_START+sp_count
            payload_ni_only ='''
<securityPolicy>
    <name> ''' + sepolicy_name + ''' </name>
    <description>Security Policy for Callback Scale</description>
    <precedence>''' + str(sepolicy_pred) + '''</precedence>
    <clientHandle></clientHandle>
    <extendedAttributes/>
    <isUniversal>false</isUniversal>
    <universalRevision>0</universalRevision>
    <inheritanceAllowed>false</inheritanceAllowed>
<actionsByCategory>
  <category>traffic_steering</category>
  <action class="trafficSteeringSecurityAction">
    <name>inbound</name>
    <clientHandle></clientHandle>
    <isUniversal>false</isUniversal>
    <universalRevision>0</universalRevision>
    <category>traffic_steering</category>
    <executionOrder>1</executionOrder>
    <isEnabled>true</isEnabled>
    <isActionEnforced>false</isActionEnforced>
    <logged>false</logged>
    <serviceProfile>
      <objectId>'''+ serviceprofile_obj_id + '''</objectId>
    </serviceProfile>
    <invalidServiceProfile>false</invalidServiceProfile>
    <redirect>true</redirect>
    <direction>outbound</direction>
    <outsideSecondaryContainer>false</outsideSecondaryContainer>
    <invalidSecondaryContainers>false</invalidSecondaryContainers>
    <applications>
      <application>
        <objectId>application-103</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>ICMP Destination Unreachable</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>ICMP</applicationProtocol>
          <value>destination-unreachable</value>
        </element>
      </application>
      <application>
        <objectId>application-105</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>ICMP Echo</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>ICMP</applicationProtocol>
          <value>echo-request</value>
        </element>
      </application>
      <application>
        <objectId>application-185</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>Syslog (TCP)</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>TCP</applicationProtocol>
          <value>514</value>
        </element>
      </application>
      <application>
        <objectId>application-226</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>ICMP Redirect</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>ICMP</applicationProtocol>
          <value>redirect</value>
        </element>
      </application>
      <application>
        <objectId>application-250</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>Syslog (UDP)</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>UDP</applicationProtocol>
          <value>514</value>
        </element>
      </application>
    </applications>
    <invalidApplications>false</invalidApplications>
  </action>
  <action class="trafficSteeringSecurityAction">
    <name>outbound</name>
    <clientHandle></clientHandle>
    <isUniversal>false</isUniversal>
    <universalRevision>0</universalRevision>
    <category>traffic_steering</category>
    <executionOrder>2</executionOrder>
    <isEnabled>true</isEnabled>
    <isActionEnforced>false</isActionEnforced>
    <logged>false</logged>
    <serviceProfile>
      <objectId>'''+ serviceprofile_obj_id + '''</objectId>
    </serviceProfile>
    <invalidServiceProfile>false</invalidServiceProfile>
    <redirect>true</redirect>
    <direction>inbound</direction>
    <outsideSecondaryContainer>false</outsideSecondaryContainer>
    <invalidSecondaryContainers>false</invalidSecondaryContainers>
    <applications>
      <application>
        <objectId>application-103</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>ICMP Destination Unreachable</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>ICMP</applicationProtocol>
          <value>destination-unreachable</value>
        </element>
      </application>
      <application>
        <objectId>application-185</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>Syslog (TCP)</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>TCP</applicationProtocol>
          <value>514</value>
        </element>
      </application>
      <application>
        <objectId>application-226</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>ICMP Redirect</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>ICMP</applicationProtocol>
          <value>redirect</value>
        </element>
      </application>
      <application>
        <objectId>application-250</objectId>
        <objectTypeName>Application</objectTypeName>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>Syslog (UDP)</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>UDP</applicationProtocol>
          <value>514</value>
        </element>
      </application>
      <application>
        <objectId>application-57</objectId>
        <objectTypeName>Application</objectTypeName>
        <revision>1</revision>
        <type>
          <typeName>Application</typeName>
        </type>
        <name>ICMP Echo Reply</name>
        <scope>
          <id>globalroot-0</id>
          <objectTypeName>GlobalRoot</objectTypeName>
          <name>Global</name>
        </scope>
        <clientHandle></clientHandle>
        <extendedAttributes/>
        <isUniversal>false</isUniversal>
        <universalRevision>0</universalRevision>
        <inheritanceAllowed>true</inheritanceAllowed>
        <element>
          <applicationProtocol>ICMP</applicationProtocol>
          <value>echo-reply</value>
        </element>
      </application>
    </applications>
    <invalidApplications>false</invalidApplications>
  </action>
</actionsByCategory>
</securityPolicy>'''

            #print(payload)
            '''
            onesp_filename = constants.INPUT_PATH + constants.SP_POLICY_PAYLOAD_NI_FILENAME
            file = open(onesp_filename, 'r')
            text = file.read()
            file.close()
            print(text)
            return False;
            '''
            myxmlheaders = {'content-type': 'application/xml'}
            start = time.clock()
            try:
                #change payload as appropriate
                response = requests.post(nsx_url, data=payload_ni_only, headers=myxmlheaders,
                                         auth=(constants.USERNAME, constants.PASSWORD), verify=False)
            except requests.exceptions.ConnectionError as e:
                print ("Connection error!")
            end = time.clock()
            elapsed_time = end - start
            timefile.write(str(sp_count) + ',' + str(elapsed_time) + '\n')
            total_elapsed_time += elapsed_time

            if (response.status_code == 201):
                sp_obj_id = response.text
                sp_success_cnt +=1
                #print("CREATED SP " + sepolicy_name + " object-id = " + sp_obj_id)
                logging.info("CREATED SP " + sepolicy_name + " object-id = " + sp_obj_id)
            else:
                #print("ERROR: CREATING SP " + sepolicy_name  + " status code = " + str(response.status_code))
                logging.error("CREATING SP " + sepolicy_name  + " status code = " + str(response.status_code))
                sp_fail_cnt +=1

        print ("SP CREATION : success_count=" + str(sp_success_cnt) + " failure_count="+ str(sp_fail_cnt))
        print ("TOTAL SP CREATION time is : " + str(total_elapsed_time) + " seconds ...")
        logging.info("SP CREATION : success_count=" + str(sp_success_cnt) + " failure_count="+ str(sp_fail_cnt))
        logging.info("TOTAL SP CREATION time is : " + str(total_elapsed_time) + " seconds ...")

        timefile.close()
        logging.debug("EXIT")
        return True


    def cb_scale_sec_policy_query_and_delete_all(self):
        logging.debug("ENTER")

        #Query all
        api_path = 'api/2.0/services/policy/securitypolicy/all'
        nsx_url = constants.NSX_URL + api_path
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")

        jdata = response.json()
        sepolicies = jdata['policies']

        #Delete all
        api_path = 'api/2.0/services/policy/securitypolicy/'
        nsx_url = constants.NSX_URL + api_path

        for sepolicy in sepolicies:
            sp_name = sepolicy['name']
            #print(sp_name)
            if (sp_name.startswith(constants.SP_NAME_PREFIX)):
                sp_obj_id = sepolicy['objectId']
                #print(sp_name + " " + sp_obj_id)
                myurl = nsx_url + sp_obj_id.__str__() + '?force=true'
                try_more = True
                try_count = 0
                while (try_more and try_count < constants.NUM_RETRIES):
                    try_more = False
                    try_count +=1
                    time.sleep(try_count*constants.WAIT_IN_SEC)
                    try:
                        response = requests.delete(myurl, headers=myheaders,
                                                 auth=(constants.USERNAME,constants.PASSWORD), verify=False)
                    except requests.exceptions.ConnectionError as e:
                        print ("Connection error!")
                    if (response.status_code == 200 or response.status_code == 204):
                        #print "DELETED SP " + sp_obj_id
                        logging.info("DELETED SP " + sp_obj_id)
                    elif (response.status_code == 500):
                        logging.info("RE-TRY DELETING SP " + sp_obj_id)
                        try_more = True
                    else:
                        #print "ERROR: DELETING SP " + sp_obj_id + " status code = "+ str(response.status_code)
                        logging.error("DELETING SP " + sp_obj_id + " status code = "+ str(response.status_code))

        logging.debug("EXIT")

        return True

    def cb_scale_sec_policy_apply(self):
        logging.debug("ENTER")

        #Query all policies
        api_path = 'api/2.0/services/policy/securitypolicy/all'
        nsx_url = constants.NSX_URL + api_path
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")

        jdata = response.json()
        sepolicies = jdata['policies']

        #Query and get all security-groups
        api_path = 'api/2.0/services/securitygroup/scope/globalroot-0'
        nsx_url = constants.NSX_URL + api_path
        #print(nsx_url)
        try:
            response = requests.get(nsx_url, headers=myheaders,
                                     auth=(constants.USERNAME,constants.PASSWORD), verify=False)
        except requests.exceptions.ConnectionError as e:
            print ("Connection error!")

        segroups = response.json()

        #PUT /api/2.0/services/policy/securitypolicy/{ID}/sgbinding/{securityGroupId}

        api_path = 'api/2.0/services/policy/securitypolicy/'
        nsx_url = constants.NSX_URL + api_path

        sp_apply_time_fname = constants.OUTPUT_PATH + constants.CB_SP_APPLY_TIME_FILE

        timefile = open(sp_apply_time_fname, "w")
        total_elapsed_time = 0
        sp_count = 0
        for sg_item, sp_item in zip(segroups, sepolicies):
            sg_name = sg_item['name']
            sg_obj_id = sg_item['objectId']
            if (not sg_name.startswith(constants.SG_NAME_PREFIX)):
                continue
            sp_name = sp_item['name']
            sp_obj_id = sp_item['objectId']
            if (not sp_name.startswith(constants.SP_NAME_PREFIX)):
                continue
            #print(sg_name, sg_obj_id, sp_name, sp_obj_id)
            #print("Total sp_count = " + str(sp_count))

            #print(sg_obj_id, sp_obj_id)
            #Add delay
            time.sleep(constants.WAIT_IN_SEC)
            sp_count += 1
            myurl = nsx_url + sp_obj_id.__str__() + '/sgbinding/' + sg_obj_id.__str__()
            #print myurl
            try_more = True
            try_count = 0
            while (try_more and try_count < constants.NUM_RETRIES):
                try_more = False
                try_count += 1
                time.sleep(try_count * 2 * constants.WAIT_IN_SEC)
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
                    #print("APPLIED SP " + sp_obj_id + " TO " + sg_obj_id)
                    logging.info("APPLIED SP " + sp_obj_id + " TO " + sg_obj_id)
                elif (response.status_code == 500):
                    logging.info("RE-TRY APPLING SP " + sp_obj_id + " TO " + sg_obj_id)
                    try_more = True
                else:
                    #print("ERROR: APPLYING SP " + sp_obj_id + " status code = " + str(response.status_code))
                    logging.error("APPLYING SP " + sp_obj_id + " status code = " + str(response.status_code))
        print("TOTAL SP APPLY Count is : " + str(sp_count))
        print ("TOTAL SP APPLY time is : " + str(total_elapsed_time) + " seconds ...")
        logging.info("TOTAL SP APPLY time is : " + str(total_elapsed_time) + " seconds ...")
        timefile.close()
        logging.debug("EXIT")

        return True

    def cb_scale_config_setup(self, input_fname, scale_count):
        print ("Started Callback Scale Setup...")
        logging.debug("ENTER")

        ret = self.cb_scale_sec_group_create(input_fname, scale_count)
        if ret != True:
            print ("ERROR: SE Group Create")

        ret = self.cb_scale_sec_policy_create_xml()
        if ret != True:
            print ("ERROR: SE Policy Create")

        ret = self.cb_scale_sec_policy_apply()
        if ret != True:
            print ("ERROR: SE Policy Apply")

        print("Completed Callback Scale Setup. Done")
        logging.debug("EXIT")

        return True

    def cb_scale_config_cleanup(self):
        print ("Started Callback Scale Cleanup...")
        logging.debug("ENTER")

        ret = self.cb_scale_sec_policy_query_and_delete_all()
        if ret != True:
            print ("ERROR: SE Policy Delete")

        ret = self.cb_scale_sec_group_query_and_delete_all()
        if ret != True:
            print ("ERROR: SE Group Delete")

        print ("Completed Callback Scale Cleanup. Done")
        logging.debug("EXIT")

        return True