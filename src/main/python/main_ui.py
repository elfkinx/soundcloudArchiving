import tkinter
from tkinter import messagebox
import main.python.scdownload as scdownload

class MainUI:
    window = tkinter.Tk()
    window.title("scdownload")
    window.geometry("800x500")
    url_label = tkinter.Label(window, text="SoundCloud URL")
    url_input = tkinter.Entry(window)
    download_button = tkinter.Button(window, text="Download")

    def custom_artist_fn(self):
        return ""

    def download_button_click(self, event):
        result = scdownload.download(self.url_input.get(), self.custom_artist_fn)
        tkinter.messagebox.showinfo("Alert", "Downloaded with result: "+ str(result))
        return "break" # required or button remains sunken after click

    def layout(self):
        self.url_label.grid(row=0,column=0)
        self.url_input.grid(row=0,column=1)
        self.download_button.grid(row=0,column=2)

    def bind_handlers(self):
        self.download_button.bind("<Button-1>", self.download_button_click)

    def run_ui(self):
        self.layout()
        self.bind_handlers()
        self.window.mainloop()


ui = MainUI()
ui.run_ui()
