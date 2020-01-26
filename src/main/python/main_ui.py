import tkinter
from cefpython3 import cefpython as cef
import os
from main.python.download_ui import DownloadUI
from main.python.files_ui import FilesUI

class MainUI:
    window = tkinter.Tk()
    window.title("scdownload")
    window.state('zoomed')
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1,uniform="row0")
    window.columnconfigure(1, weight=1,uniform="row0")

    left = tkinter.Frame(window,borderwidth=1,relief="solid")
    right = tkinter.Frame(window,borderwidth=1,relief="solid")

    download_ui = DownloadUI(left)
    files_ui = FilesUI(right)

    def run_ui(self):
        self.left.grid(row=0,column=0,sticky='nsew')
        self.right.grid(row=0,column=1,sticky='nsew')
        cef.Initialize()
        # cef.MessageLoop()
        tkinter.mainloop()
        cef.Shutdown()


ui = MainUI()
ui.run_ui()
