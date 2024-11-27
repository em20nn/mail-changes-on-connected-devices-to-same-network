import subprocess
import requests
import smtplib
import time
from email.mime.text import MIMEText
import ssl
import re
from collections import deque

SMTP_SERVER = 'smtp.gmail.com' # SMTP server
SMTP_PORT = 465  # Port for SSL
SMTP_USER = ''  # Your Gmail address
SMTP_PASSWORD = ''   # Your App Password
EMAIL_RECIPIENT = ''

MAC_NAME_MAP = {
    'AA:AA:AA:AA:AA:AA': 'NAME',
}

def send_notification(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_RECIPIENT

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_connected_devices():
    checkpoint=True
    while checkpoint:
        try:
            output = subprocess.check_output(['/usr/sbin/arp-scan', '--localnet'], universal_newlines=True)
            devices = []
            for line in output.splitlines():
                match = re.search(r'([0-9a-fA-F:]{17})\s+', line)
                if match:
                    mac_address = match.group(1)
                    devices.append(mac_address)
            if devices!=[]:
                checkpoint=False
                return devices
            else:
                time.sleep(1)
        except Exception as e:
            print(f"Error retrieving devices: {e}")
            time.sleep(1)

def log():
    aa=[]
    for _ in range(5):
        scan_result=get_connected_devices()
        for i in scan_result:
            aa.append(i)
        time.sleep(1)
    aa_purge=list(set(aa))
    return aa_purge

def main():
    th5_old_scan=[]
    th4_old_scan=[]
    th3_old_scan=[]
    nd2_old_scan=[]
    st1_old_scan=[]
    current_scan=[]
    message_lines=[]
    connected=[]
    disconnected=[]
    while True:
        try:
            if log()!=[]:
                current_scan=log()
                for i in current_scan:
                    if i in st1_old_scan:
                        continue
                    elif i in nd2_old_scan:
                        continue
                    elif i in th3_old_scan:
                        continue
                    elif i in th4_old_scan:
                        continue
                    elif i in th5_old_scan:
                        continue
                    else:
                        connected.append(i)
                for i in th5_old_scan:
                    if i in current_scan:
                        continue
                    elif i in st1_old_scan:
                        continue
                    elif i in nd2_old_scan:
                        continue
                    elif i in th3_old_scan:
                        continue
                    elif i in th4_old_scan:
                        continue
                    else:
                        disconnected.append(i)
                th5_old_scan=th4_old_scan
                th4_old_scan=th3_old_scan
                th3_old_scan=nd2_old_scan
                nd2_old_scan=st1_old_scan
                st1_old_scan=list(current_scan)
                if connected!=[]:
                    message_lines.append("New devices connected:\n" +
                                     "\n".join(f"{mac} - {MAC_NAME_MAP.get(mac, '')}" for mac in connected))
                if disconnected!=[]:
                    message_lines.append("Devices disconnected:\n" +
                                     "\n".join(f"{mac} - {MAC_NAME_MAP.get(mac, '')}" for mac in disconnected))
                if message_lines!=[]:
                    message_lines.append("\n---" + "\nCurrent devices connected:\n" +
                                     "\n".join(f"{mac} - {MAC_NAME_MAP.get(mac, '')}" for mac in list(set(st1_old_scan+nd2_old_scan+th3_old_scan+th4_old_scan+th5_old_scan))))
                    message_content = "\n\n".join(message_lines)
                    send_notification("Wi-Fi Notification", message_content)
                connected=[]
                disconnected=[]
                current_scan=[]
                message_lines=[]
                time.sleep(20)
            else:
                print("Returned empty")
                time.sleep(20)
        except Exception as e:
            print(f"ERR {e}")
            time.sleep(20)

if __name__ == '__main__':
    main()