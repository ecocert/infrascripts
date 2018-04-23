import requests
from requests.auth import HTTPBasicAuth

class CertClient:

    def __init__(self):
        self.base_url = 'http://10.148.254.1:8080/devops/webapi'
        #self.base_url = 'http://127.0.0.1:9090/devops/webapi'
        self.ip_address_discovery_url = 'http://10.148.172.7/hermes/show-ip.php'
        print ("cert client")


    def getJob(self, jobid):
        url = self.base_url + '/jobs/'+str(jobid)
        r = requests.get(url,auth=HTTPBasicAuth('test_bed_tissa', 'VMware1!'))
        if(r.status_code == 302):
            # print (r.json())
            return r.json()
        else:
            print ("object not found ")

    def requestScale(self, userName, operation, certName, ipAddress):
        jobid = -1
        payload={
                  "userName": userName,
                  "jobCategory": "SCALE",
                  "jobType" : "ESXSCALE",
                  "jobPriority":"HIGH",
                  "jobOperation": operation,
                  "certName": certName,
                  "externalIPAddress": ipAddress
                }
        url=self.base_url+'/jobs'

        r=requests.post(url,json=payload, auth=HTTPBasicAuth('test_bed_tissa', 'VMware1!'))
        print(" Status CCOde 8*** {0}".format(r.status_code))
        body = r.json()

        return body['jobID']

    def getipaddress(self):
        r = requests.get(self.ip_address_discovery_url)
        if r.status_code == 200:
            ipaddress=r.text

            return ipaddress

    def checkJobDone(self, jobid):
        resp = self.getJob(jobid)
        if(resp):
            if 'state' in resp and resp['state'] == 'DONE':
                print("Job is done")
                return True

        return False


    def requestIxia(self, userName, operation, certName, ipAddress):
        jobid = -1
        payload={
                  "userName": userName,
                  "jobCategory": "RESOURCE",
                  "jobType" : "IXIALICENCE",
                  "jobPriority":"HIGH",
                  "jobOperation": operation,
                  "certName": certName,
                  "externalIPAddress": ipAddress
                }
        url=self.base_url+'/jobs'
        r=requests.post(url,json=payload,auth=HTTPBasicAuth('test_bed_tissa', 'VMware1!'))
        body = r.json()

        return body['jobID']

    def connectH(self, a):
        print ("test program" , a)

    def main(self):
        self.connectH(a="Hello")






