from dotenv import load_dotenv
import imaplib
import datetime
import email
import re
import time
import os
import requests

load_dotenv()

today = datetime.date.today().strftime("%d-%b-%Y")
EMAIL = os.getenv('EMAIL')
PASS = os.getenv('EMAIL_PASSWORD')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
IMAP_SERVER = os.getenv('IMAP_SERVER')


def get_otp_from_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL,PASS)
    mail.select('inbox')

    result, data = mail.search(None,f'(SINCE "{today}")')

    mail_ids = data[0].split()
    latest_ids = mail_ids[-10:]
    subject = None

    for num in reversed(latest_ids):
        result, msg_data = mail.fetch(num,'(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        subject = msg['subject']
        if("OTP" in subject or 'otp' in subject.lower()):
            if(msg.is_multipart()):
                body = msg.get_payload(0).get_payload(decode=True).decode()
                otp_match = re.search(r'\b\d{4,6}\b',body)
                if(otp_match):
                    otp = otp_match.group(0)
                    mail.store(num,'+FLAGS','\\Seen')
                    return otp

def send_otp_to_telegram(otp):
    print(otp)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id":CHAT_ID,
        "text":f"OTP Recieved:{otp}"
    }
    print(data)
    
    response = requests.post(url, data=data)

def main():
    otp = get_otp_from_email()
    if(otp):
        send_otp_to_telegram(otp)
        time.sleep(10)
    time.sleep(10)

if(__name__ == '__main__'):
    main()