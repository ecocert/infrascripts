from CertClient import CertClient
import time

user_name = "Tissa"
cert_name = "netx_6.3"

def menu():
    c = CertClient()
    while(True):
        print("1. Request ESX For scale :")
        print("2. Remove ESX Scale")
        print("3. Request IXIA resources")
        print("4. Remove IXIA resources ")
        print("5. Check Status of Job")
        print("6. Wait for Job finish")
        print("7. Quit")
        menuid = input("Enter Your Choice:  ")
        test_bed_ip = c.getipaddress()
        print("IP Address {0}".format(test_bed_ip))
        jobid = -1
        if(menuid == str(1)):
            jobid = c.requestScale(user_name, "ADD", cert_name, test_bed_ip)
        elif (menuid == str(2)):
            jobid = c.requestScale(user_name, "REMOVE", cert_name, test_bed_ip)
        elif (menuid == str(3)):
            jobid = c.requestIxia(user_name, "ADD", cert_name, test_bed_ip)
        elif (menuid == str(4)):
            jobid = c.requestIxia(user_name, "REMOVE", cert_name, test_bed_ip)
        elif (menuid == str(5)):
            try:
                jobid = int (input("Enter Job ID: "))
                resp = c.getJob(jobid)
                if (resp and 'state' in resp):
                    print("Job state is {0}".format(resp['state']))
                else:
                    print("job not available ")
            except (TypeError, ValueError) as e:
                print("invalid entry has to be an integer", e)


        elif (menuid == str(6)):
            try:
                jobid = int(input("Enter Job ID: "))
                while (True):
                    if (c.checkJobDone(jobid)):
                        print("job {0} is done".format(jobid))
                        break;
                    else:
                        print('.', end='', flush=True)
                        time.sleep(30)
            except (TypeError, ValueError) as e:
                print("invalid entry has to be an integer", e)



        elif (menuid == str(7)):
            return
        else:
            print (" -------------------")
            print("invalid choice try again \n")
        if(jobid != -1):
            print("jobID is {0}".format(jobid))


def main():
    c = CertClient()
    print("Hello test")
    c.main()
    # c.checkJobDone(900)

    menu()
    return


    test_bed_ip = c.getipaddress()

    jobid = c.requestScale("test_bed_tissa","REMOVE","scale_netx_6.3", test_bed_ip)

    print ("JobID {0} - status {1}".format(jobid, c.checkJobDone(jobid)) )
    while(True):
        print ("State - {0}".format(c.checkJobDone(jobid)) )
        if (c.checkJobDone(jobid)):
            break
        time.sleep(30)


if __name__ == '__main__':
    main()