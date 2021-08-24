import schedule 
import time
#import Need2Input_Revision as Need
from datetime import date, datetime

import win32com.client
from datetime import date, datetime
import pandas as pd
import openpyxl
from outlook_send import send_email

def PendingEntry():
    #Get today's date and time
    today = date.today()
    now = datetime.now()
    now_str = str(now)[0:16]
    #Open Outlook
    outlook=win32com.client.Dispatch("Outlook.Application").GetNameSpace("MAPI")

    #Grab Specific Folder
    #inbox=outlook.GetDefaultFolder(6) #Inbox default index value is 6
    Need2Input=outlook.GetDefaultFolder(6).Folders.Item("Need to Input")
    Revision=outlook.GetDefaultFolder(6).Folders.Item("Revisions")

    #Count Items in Inbox
    #N2I_count = Need2Input.Items.Count
    #Rev_count = Revision.Items.Count

    #print(N2I_count)
    #print(Rev_count)


    #Access Subject, Date, Body, etc.
    N2I_message=Need2Input.Items
    message=N2I_message.GetLast()

    Rev_message=Revision.Items
    message2=Rev_message.GetLast()



    #item_count = message2.Items.Count
    #subject=message2.Subject
    #body=message2.body
    #date=message2.senton.date()
    #sender=message2.Sender
    #attachments=message2.Attachments
    #print(item_count)

    #Create Excel Sheet
    fname = 'PendingEntry.xlsx'
    f = open(fname,'w+')
    f.write("Need to Input\n")

    #Iterate for items in folder with specific condition
    #print('\nNeed to Input')
    for message in N2I_message:
        #if message.senton.date() == today:
        #print(message.subject)

        f.write(message.subject.replace(',','&') + '\n')
        #print(message.senton.date())
        #print(message.senton.time())

    f.close()

    #drop duplicates
    N2I_data = pd.read_csv('PendingEntry.xlsx')
    upper_data = N2I_data.apply(lambda x: x.astype(str).str.upper())
    new_data = upper_data.drop_duplicates()
    hide_data = new_data.to_string(index=False)
    #print(hide_data)


    #Create Excel Sheet
    fname = 'Revision.xlsx'
    f = open(fname,'w+')
    f.write("\n\nRevisions\n")
    #print('\nRevisions') 
    for message2 in Rev_message:
        #if message.senton.date() == today:
        f.write(message2.subject.replace(',','&') + '\n')
        #print(message2.subject)

    f.close()

    #drop duplicates
    Rev_data = pd.read_csv('Revision.xlsx')
    upper_data2 = Rev_data.apply(lambda x: x.astype(str).str.upper())
    new_data2 = upper_data2.drop_duplicates()
    hide_data2 = new_data2.to_string(index=False)
    #print(hide_data2)

    N2I_count = len(new_data)
    Rev_count = len(new_data2)

    # Pass arguments below in following order: To Address, Subject, Email Body, Path to file to attach
    send_email('sokchu@boalogistics.com, data@boalogistics.com ,reefer@boalogistics.com, julie@boalogistics.com, daigo@boalogistics.com, wlopes@boalogistics.com, mmugar@boalogistics.com' ,
               'Pending Entry Report ' + now_str,
               'Hello Team,\n\nPlease see current entry queue.\n\nNew Orders: ' + str(N2I_count) + '\n\nRevisions: '+ str(Rev_count) + '\n\n' + hide_data + '\n\n\n' + hide_data2 + '\n\n Thank you,\n\nSokchu Hwang')

#reefer@boalogistics.com, julie@boalogistics.com, daigo@boalogistics.com, wlopes@boalogistics.com, mmugar@boalogistics.com'
    
now_str = str(datetime.now())[11:13]
now = int(now_str)
    
schedule.every(30).minutes.do(PendingEntry)

print('Sending')

while now > 8 & now < 17:
    schedule.run_pending()

print('Sent')
    
    