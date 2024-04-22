#! /usr/bin/python3
import json
import sys
import os
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText

SMTPserver = os.getenv('SMTP_SERVER')
sender = os.getenv('SENDER')
destination = json.loads(os.getenv('DESTINATION'))

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv("PASSWORD")


def main(content: str, subject: str):
    # typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'

    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = sender  # some SMTP servers will do this automatically, not all

        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.quit()

    except:
        sys.exit("mail failed; %s" % "CUSTOM_ERROR")  # give an error message


if __name__ == '__main__':
    subject_text = sys.argv[1]
    message_text = sys.argv[2]
    main(message_text, subject_text)
