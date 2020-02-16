import tkinter
from cefpython3 import cefpython as cef
from main.python.download_ui import DownloadUI
from main.python.files_ui import FilesUI

"""
scdownload (SoundCloud Downloader)

This file defines the main GUI wrapper for the application

"""

class MainUI:
    window = tkinter.Tk()
    # Set the window bar title to 'scdownload'
    window.title("scdownload")
    # This makes the page maximised to begin with
    window.state('zoomed')
    window.configure(background="#FFF")
    # This sets the internal content to expand to fit the container  by default
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
        # cef (to preview the page) must be initialized before the main UI loop
        cef.Initialize()
        # Run the main UI loop
        tkinter.mainloop()
        cef.Shutdown()

# The entry point for the GUI application
ui = MainUI()
ui.run_ui()
