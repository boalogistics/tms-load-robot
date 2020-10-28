

"""
ZetCode Tkinter tutorial

In this script, we use the grid
manager to create a more complicated Windows
layout.

Author: Jan Bodnar
Website: www.zetcode.com
"""

from tkinter import Tk, Text, BOTH, W, N, E, S
from tkinter.ttk import Frame, Button, Label, Style, Radiobutton


class Example(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.master.title("Windows")
        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = Label(self, text="Windows")
        lbl.grid(sticky=W, pady=4, padx=5)

        area = Text(self)
        area.grid(
            row=1,
            column=0,
            columnspan=2,
            rowspan=4,
            padx=5,
            sticky=E+W+S+N
        )

        actionlbl = Label(self, text="Select action below:")
        actionlbl.grid(row=1, column=3)
        
        rbtn1 = Radiobutton(self, text="Price", value="pricer")
        rbtn1.grid(row=2, column=3)

        rbtn2 = Radiobutton(self, text="Upload POD", value="pod_upload")
        rbtn2.grid(row=3, column=3)

        rbtn3 = Radiobutton(self, text="Something Else", value="something")
        rbtn3.grid(row=4, column=3)

        hbtn = Button(self, text="Help")
        hbtn.grid(row=5, column=0, padx=5)

        qbtn = Button(self, text="Exit", command=self.quit)
        qbtn.grid(row=5, column=3)


def main():

    root = Tk()
    root.geometry("350x300+300+300")
    app = Example()
    root.mainloop()


if __name__ == '__main__':
    main()