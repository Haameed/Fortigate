from fortiosapi import FortiOSAPI
from datetime import datetime
import time
import os

import sys

Last_used = 30 # days

def check_key(dict,key):
    if key in dict.keys():
        return True
    else:
        return False

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

receivers = ["contact1@mycompany.com" , "contact1@mycompany.com"]

def send_test_mail(contact , body):
    sender_email = "notifier@mycompany.com"
    receiver_email = contact

    msg = MIMEMultipart()
    msg['Subject'] = 'Fortigate unused Policy list'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msgText = MIMEText(body)
    msg.attach(msgText)
    attachment = open(log_path,encoding="utf-8").read()
    attachment = MIMEText(attachment)
    attachment.add_header('content-disposition', 'attachment', filename='result.txt')
    msg.attach(attachment)
    msg.add_header('content-disposition', 'attachment', filename='result.txt')
    with smtplib.SMTP('mail.mycompany.com', 587) as smtpObj:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login("notifier@mycompany.com", "password")
        smtpObj.sendmail(sender_email, receiver_email, msg.as_string())


start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
file_name = f'Not_used_policies_{datetime.now().strftime("%Y-%m-%d")}.log'
log_path = rf'/usr/share/python_scripts/logs/{file_name}'
log = open(log_path, 'a+')
log.write(f"---------- Check started at {start} ----------\n")

connection = FortiOSAPI()
try:
    coneection = connection.login(host="firewall-ip", username="username", password="password", verify=False)
    policy_list = connection.monitor(vdom='root', path="firewall", name="policy")
    time_threshold = Last_used * 24 * 60 *60
    current = time.localtime()
    zero_hit_count = ""
    old_policies = ""
    for i in range(len(policy_list["results"])):
        current = round(time.time())
        policy = policy_list["results"][i]
        policyid = policy["policyid"]
        first_used = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(policy["first_used"])) if check_key(policy,"first_used") else "N/A"
        last_used = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(policy["last_used"])), policy["last_used"]] if check_key(policy, "last_used") else ["N/A","N/A"]
        hit_count = int(policy["hit_count"]) if check_key(policy,"hit_count") else 0
        if hit_count == 0:
            zero_hit_count += f"Policy {policyid} Last_used = {last_used[0]}\n"
        if last_used[1] != "N/A" and current - last_used[1] > time_threshold:
            old_policies += f"policy {policyid} Last_used = '{last_used[0]}' with {hit_count} hit counts \n"
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if zero_hit_count:
        log.write(f'############################ Policy/ies with Zero hit count ############################\n')
        log.write(f"{zero_hit_count}\n")
    if old_policies:
        log.write(f'############################ Policy/ies which has not used in last {Last_used} days ############################\n')
        log.write(f"{old_policies}\n")
    log.write(f"---------- Check finished at {end} ----------\n")

except:
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.write(f"could not connect to fortigate\n")
    log.write(f"---------- Check finished at {end} ----------\n")
finally:
    log.close()
    if zero_hit_count or old_policies:
        for contact in receivers:
            send_test_mail(contact,f"Find policy which has not been used over last {Last_used} days or have zero hit count. Please find the attachment.")
