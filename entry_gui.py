import tkinter as tk
import os
import tkinter.font as tkFont
from tkinter import messagebox

def getlist():
    # list of text to filter out
    FILTERS = ['Master', 'Single', 'Consol', 'Please', 'Hello ']
    text = entry.get('1.0', tk.END)
    res_list = (text.rstrip().split('\n')) 
    print('Raw input: \n', res_list)
    res_list = [item[:6] for item in res_list]
    print('Parsing first 6 characters...\n', res_list)

    print('Checking for invalid load numbers...\n')
    
    try:
        int_check = [int(i) for i in res_list]
        messagebox.showinfo('Success!', 'Input values all integers.')
    except Exception as e:
        messagebox.showinfo('Attention Needed!', 'Non-integer values found.Check output for accuracy.')

    res_list_int = []
    for i in res_list:
        try:
            int(i)
            res_list_int.append(i)
        except Exception as e:
                print(f'{i} is not an integer.')
  
    if all(len(i) == 6 for i in res_list_int):
        print('probably all valid load numbers!')
    else:
        print('invalid load numbers present!')
    
    output = "['" + "', '".join(res_list_int) + "']"

    print(output)

    f = open('loadnos.txt', 'w')
    f.write(output)
    f.close()

    os.startfile('loadnos.txt')


window = tk.Tk()
window.title('Load Bot')
window.option_add('*Font', 'SegoeUI')
# window.Text.configure(font=(family='SegoeUI', fg='white'), bg='grey')

frame_top = tk.Frame()

title = tk.Label(
    master=frame_top,
    text='Enter load numbers below, each separated on a new line.',
    font='12',
    height=2
)
title.pack()

frame_mid = tk.Frame(
    master=window, 
    relief=tk.SUNKEN, 
    borderwidth=2
)

scrollbar = tk.Scrollbar(frame_mid)
scrollbar.pack(
    side = tk.RIGHT, 
    fill = tk.Y
)

entry = tk.Text(
    master=frame_mid, 
    bd=0, 
    height=25, 
    width=40,
    yscrollcommand = scrollbar.set
)
entry.pack()


frame_btm = tk.Frame()

button = tk.Button(
    master=frame_btm,
    text='Next',
    width=10,
    height=1,
    command=getlist
)
button.pack()

frame_top.pack(padx = 5, pady=5)
frame_mid.pack(padx = 5, pady=5)
frame_btm.pack(padx = 5, pady=5)

scrollbar.config(command = entry.yview)

window.mainloop()