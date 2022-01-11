from netmiko import ConnectHandler
import datetime
import time
import os
import subprocess


servers = { "main": {"name": "fortinet_main", "ip":"ip_address", "username": "myuser", "password": "mypass" , "ftp_user": "ftp", "ftp_pass": "ftppassword", "encryption_pass": "somencryptionpass" },
            "secondary": {"name": "fortinet_seondary", "ip":"ip_address", "username": "myuser", "password": "mypass" , "ftp_user": "ftp", "ftp_pass": "ftppassword", "encryption_pass": "somencryptionpass" }
            }
contact_points=["myphone_number"]
remote_ftp = 'ftp_ip_address'
log_path=r'/usr/share/python_scripts/backup.log'


def backup_job(server):
    log = open(log_path, 'a')
    log.write(f"----------- starting bachup job for {server['name']} {datetime.datetime.today().strftime('%Y%m%d %H:%M')} ----------- \n")
    fw = {"host": server["name"], "device_type": "fortinet", "ip": server["ip"], "username": server["username"],
          "password": server["password"] }
    file_name = f"{fw['host']}_{datetime.datetime.today().strftime('%Y%m%d_%H%M')}.comf"
    net_conn = ConnectHandler(**fw)
    net_conn.send_command('config vdom', expect_string='$')
    net_conn.send_command('edit root', expect_string='$')
    time.sleep(1)
    output = net_conn.send_command(
        f'execute backup full-config ftp {file_name} {remote_ftp} {server["ftp_user"]} {server["ftp_pass"]} {server["encryption_pass"]}',
        cmd_verify=False)
    """ output = net_conn.send_command(f'execute backup full-config ftp {file_name} {remote_ftp}
     {server["ftp_user"]} {server["ftp_pass"]}', cmd_verify=False)"""
    log.write(output)
    if "Send config file to ftp server OK." in output:
        message = "backup finished successfully."
        log.write(f"{message}\n")
        log.write("\n \n")
    else:
        message = "backup failed."
        log.write(f"{message}\n")
        log.write("\n \n")
    log.close()
    for number in contact_points:
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/etc/init.d/apache2', 'restart'], stdout=devnull, stderr=subprocess.STDOUT)
        os.system(f'/usr/bin/python3 /usr/bin/sendsms.py -c {number} -m "backup job for {server["name"]} was executed.\n result: {message}" 2&1>/dev/null')


for key in servers:
    backup_job(servers[key])
