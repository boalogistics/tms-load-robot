import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path

def send_email(email_recipient, email_subject, email_message, attachment_location = ''):
    email_sender = 'sokchu@boalogistics.com'

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    msg.attach(MIMEText(email_message, 'plain'))

    if attachment_location != '':
        filename = os.path.basename(attachment_location)
        attachment = open(attachment_location, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.login('sokchu@boalogistics.com', 'Immuneact10!')
        text = msg.as_string()
        server.sendmail(email_sender, email_recipient, text)
        print('email sent')
        server.quit()
    except:
        print("SMTP server connection error")
    return True


# Pass arguments below in following order: To Address, Subject, Email Body, Path to file to attach
#send_email('data@boalogistics.com',
#          'Subject Test',
#           'Email body test with \n new line.', 
#           'C:\\Users\\USERNAMEHERE\\Downloads\\FILENAME HERE')