import win32com.client as win32
import datetime

today = datetime.date.today().strftime('%B %d, %Y 12:00 AM')
outlook = win32.gencache.EnsureDispatch("Outlook.Application").GetNamespace("MAPI")

# 6 assigned to main Inbox Folder
inbox = outlook.GetDefaultFolder(6)
accounting = inbox.Folders.Item('Boa').Folders.Item('Accounting')
messages = accounting.Items
relevant = messages.Restrict("[SentOn] > '{}'".format(today)).Restrict("[Subject] = 'Consols'")

print(relevant.Count)

for item in relevant:
    print(item.Subject, item.ReceivedTime)

# subjects = [message['Subject'] for message in messages]

# print(subjects)


outlook.Application.Quit()