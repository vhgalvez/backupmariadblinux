#!/usr/bin/python3

###########################################################
#
# This python script is used for mysql database backup
# using mysqldump and tar utility.
#
# Written by : Rahul Kumar
# Website: http://tecadmin.net
# Created date: Dec 03, 2013
# Last modified: Aug 17, 2018
# Tested with : Python 2.7.15 & Python 3.5
# Script Revision: 1.4
#
##########################################################

# Import required python libraries

import os
import time
import datetime
import pipes

# Import modules
import smtplib
import ssl
# email.mime subclasses
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Add new subclass for adding attachments
from email.mime.application import MIMEApplication
# The pandas library is only for generating the current date, which is not necessary for sending emails
import pandas as pd

# MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases backup.
# To take multiple databases backup, create any file like /backup/dbnames.txt and put databases names one on each line and assigned to DB_NAME variable.

DB_HOST = 'localhost'
DB_USER = 'my_user_of_database'
DB_USER_PASSWORD = 'my_passw'

DB_NAME = 'my_database'
BACKUP_PATH = 'my_path'

# Getting current DateTime to create the separate backup folder like "20180817-123433".
DATETIME = time.strftime('%Y%m%d-%H%M%S')
TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME

# Checking if backup folder already exists or not. If not exists will create it.
try:
    os.stat(TODAYBACKUPPATH)
except:
    os.mkdir(TODAYBACKUPPATH)

# Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
print("checking for databases names file.")
if os.path.exists(DB_NAME):
    file1 = open(DB_NAME)
    multi = 1
    print("Databases file found...")
    print("Starting backup of all dbs listed in file " + DB_NAME)
else:
    print("Databases file not found...")
    print("Starting backup of database " + DB_NAME)
    multi = 0

# Starting actual database backup process.
if multi:
    in_file = open(DB_NAME, "r")
    flength = len(in_file.readlines())
    in_file.close()
    p = 1
    dbfile = open(DB_NAME, "r")

    while p <= flength:
        db = dbfile.readline()   # reading database name from file
        db = db[:-1]         # deletes extra line
        dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + \
            " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
        os.system(dumpcmd)
        gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
        os.system(gzipcmd)
        p = p + 1
    dbfile.close()
else:
    db = DB_NAME
    dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + \
        " " + db + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
    os.system(gzipcmd)

print("")
print("Backup script completed")
print("Your backups have been created in '" + TODAYBACKUPPATH + "' directory")

# Define the HTML document
# Add an image element
##############################################################
html = '''
    <html>
        <body>
            <h1>Report Backup</h1>
            <p>Backup script completed</p>
            <img src='cid:myimageid' width="700">
        </body>
    </html>
    '''
##############################################################

# Define a function to attach files as MIMEApplication to the email
# Add another input extra_headers default to None
##############################################################


def attach_file_to_email(email_message, filename, extra_headers=None):
    # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
    with open(filename, "rb") as f:
        file_attachment = MIMEApplication(f.read())
    # Add header/name to the attachments
    file_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Set up the input extra_headers for img
    # Default is None: since for regular file attachments, it's not needed
    # When given a value: the following code will run
    # Used to set the cid for image
    if extra_headers is not None:
        for name, value in extra_headers.items():
            file_attachment.add_header(name, value)
    # Attach the file to the message
    email_message.attach(file_attachment)
##############################################################


# Set up the email addresses and password. Please replace below with your email address and password
email_from = 'my_email'
password = 'my_passw_email'
email_to = 'email_to'

# Generate today's date to be included in the email Subject
date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

# Create a MIMEMultipart class, and set up the From, To, Subject fields
email_message = MIMEMultipart()
email_message['From'] = email_from
email_message['To'] = email_to
email_message['Subject'] = f'Report email - {date_str}'

# Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
email_message.attach(MIMEText(html, "html"))

# Attach more (documents)
# Apply function with extra_header on chart.png. This will render chart.png in the html content
##############################################################

# attach_file_to_email(email_message, 'chart.png', {'Content-ID': '<myimageid>'})

##############################################################

# attach_file_to_email(email_message, 'excel_report.xlsx')
# attach_file_to_email(email_message, 'fpdf_pdf_report.pdf')

# Convert it as a string
email_string = email_message.as_string()

# Connect to the Gmail SMTP server and Send Email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(email_from, password)
    server.sendmail(email_from, email_to, email_string)
