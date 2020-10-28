import tkinter as tk
import os
import tkinter.font as tkFont
from tkinter import messagebox

def getlist():
    text = entry.get('1.0', tk.END)
    res_list = (text.rstrip().split('\n')) 
    print('Raw input: \n', res_list)
    res_list = [item[:6] for item in res_list]
    print('Parsing first 6 characters...\n', res_list)

    try:
        print('Checking for invalid load numbers...\n')
        res_list_int = [int(i) for i in res_list]
        messagebox.showinfo('Success!', 'Input values all integers.')
    except Exception as e:
        print(e)
        messagebox.showerror('Alert', 'Invalid values were present, please verify output for accuracy.')
    finally:
        res_list = list(filter(lambda item: len(item) == 6 and item != 'Master' and item !='Single' and item != 'Consol', res_list))
        print('Dropping invalid load numbers...\n', res_list)
    if all(len(i) == 6 for i in res_list):
        print('probably valid load numbers!')
    else:
        print('invalid load numbers!')
    
    output = "['" + "', '".join(res_list) + "']"

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
    width=80,
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