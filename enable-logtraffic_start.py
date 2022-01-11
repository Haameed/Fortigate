from fortiosapi import FortiOSAPI
from _datetime import datetime
import sys
import os

contacts = ["phonenumber1", "phonenumber2",  "phonenumber3"]

def sendsms(message):
    for contact in contacts:
        os.system(rf'/bin/sendsms.py -c {contact} -m "{message}"')

start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
file_name = f'logtraffic_{datetime.now().strftime("%Y-%m-%d")}.log'
log_path = rf'/usr/share/python_scripts/{file_name}'
log = open(log_path, 'a+')
log.write(f"---------- Check started at {start} ----------\n")
connection = FortiOSAPI()
changed_list = ""
failed_list = ""
try:
    coneection = connection.login(host="firewall-ip", username="username", password="password", verify=False)
    policy_list = connection.get(vdom='root', path="firewall", name="policy")
    for i in range(len(policy_list["results"])):
        policy_id = policy_list["results"][i]["policyid"]
        policy_name = policy_list["results"][i]["name"]
        policy_status = policy_list["results"][i]["status"]
        policy_logtraffic_start = policy_list["results"][i]["logtraffic-start"]
        if policy_status == "enable" and policy_logtraffic_start == "disable":
            data = {"logtraffic-start": "enable"}
            update = connection.put(vdom='root', path="firewall", name="policy", mkey=policy_id, data=data)
            changed = update["revision_changed"]
            update_status = update["status"]
            if changed and update_status == "success":
                log.write(f"The value of logtraffic_start has been change to enable for '{policy_name}'\n")
                changed_list += f"{policy_name}\n"
                print(changed_list)
            else:
                log.write(f"Unable to change logtraffic_start for '{policy_name}'\n")
                log.write(f"{update}\n")
                failed_list += f"{policy_name}\n"
                print(failed_list)
        else:
            log.write(f"logtraffic_start is enabled. No action is required for '{policy_name}'\n")
    connection.logout()
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.write(f"---------- Check finished at {end} ----------\n")
except:
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.write(f"could not connect to fortigate\n")
    log.write(f"---------- Check finished at {end} ----------\n")
finally:
    log.close()
    if changed_list:
        sendsms(f"Find policy with disable 'logtraffic_start'\n {changed_list}")
    if failed_list:
        sendsms(f"Find policy with disable 'logtraffic_start but could not change the status'\n {changed_list}")
