import tkinter
from tkinter import messagebox
from cefpython3 import cefpython as cef
import ctypes
import logging
import main.python.scdownload as scdownload


class DownloadUI:
    def __init__(self, parent):
        self.container = tkinter.Frame(parent,borderwidth=1,relief="solid")

        self.download_frame = tkinter.Frame(self.container,borderwidth=1,relief="solid")
        self.url_label = tkinter.Label(self.download_frame, text="SoundCloud URL")
        self.url_input = tkinter.Entry(self.download_frame)
        self.download_button = tkinter.Button(self.download_frame, text="Download")
        self.preview_button = tkinter.Button(self.download_frame, text="Preview")

        self.preview_frame = tkinter.Frame(self.container,borderwidth=1,relief="solid")
        self.browser_frame = BrowserFrame(self.preview_frame,borderwidth=1,relief="solid")
        self.preview_label = tkinter.Label(self.preview_frame, text="Preview")

        self.metadata_frame = tkinter.Frame(self.container)

        self.track_metadata_frame = tkinter.Frame(self.metadata_frame)
        self.albums_button = tkinter.Button(self.track_metadata_frame, text="Albums")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")
        self.album_button = tkinter.Button(self.track_metadata_frame, text="Album")

        self.bind_handlers()
        self.layout()

    def layout(self):
        self.container.pack(expand="yes", fill="both")
        self.container.columnconfigure(0, weight=1, uniform="col0")
        self.container.rowconfigure(0, weight=1, uniform="col0")
        self.container.rowconfigure(1, weight=8, uniform="col0")
        self.container.rowconfigure(2, weight=8, uniform="col0")
        self.container.rowconfigure(3, weight=8, uniform="col0")

        self.download_frame.grid(row=0,column=0,sticky="nsew")
        self.download_frame.rowconfigure(0, weight=1, uniform="col0")
        self.download_frame.columnconfigure(0, weight=1, uniform="row0")
        self.download_frame.columnconfigure(1, weight=1, uniform="row0")
        self.download_frame.columnconfigure(2, weight=1, uniform="row0")
        self.download_frame.columnconfigure(3, weight=1, uniform="row0")
        self.url_label.grid(row=0,column=0,sticky="nsew")
        self.url_input.grid(row=0,column=1,sticky="nsew")
        self.download_button.grid(row=0,column=2,sticky="nsew")
        self.preview_button.grid(row=0,column=3,sticky="nsew")

        self.preview_frame.grid(row=1,column=0,sticky="nsew")
        self.preview_frame.columnconfigure(0, weight=1, uniform="col0")
        self.preview_frame.rowconfigure(0, weight=1, uniform="col0")
        self.preview_frame.rowconfigure(1, weight=8, uniform="col0")
        self.preview_label.grid(row=0,column=0,sticky="nsw")
        self.browser_frame.grid(row=1,column=0,sticky="nsew")

        self.metadata_frame.grid(row=2,column=0,sticky="nsew")
        self.metadata_frame.columnconfigure(0, weight=1, uniform="col0")
        self.metadata_frame.rowconfigure(0, weight=1, uniform="row0")
        self.metadata_frame.rowconfigure(1, weight=1, uniform="row0")
        self.metadata_frame.rowconfigure(2, weight=1, uniform="row0")
        self.track_metadata_frame.grid(row=0, column=0, sticky="nsew")

    def bind_handlers(self):
        self.download_button.bind("<Button-1>", self.download_button_click)
        self.preview_button.bind("<Button-1>", self.preview_button_click)
        self.url_input.bind("<Button-1>", self.force_focus)

    def force_focus(self, event):
        event.widget.focus_force()

    def download_button_click(self, event):
        logging.info("Download button click")
        if self.url_input.get() != "":
            # TODO: Make this async so it doesn't lock up the UI
            result = scdownload.download(self.url_input.get(), self.custom_artist_fn,
                                         metadata=["playlists", "albums", "background"])
            messagebox.showinfo("Alert", "Downloaded with result: " + str(result))
            # TODO: Make file tree view refresh on new downloads
        else:
            logging.info("Ignoring download click due to empty input")
        # return "break"  # required or button remains sunken after click

    def preview_button_click(self, event):
        logging.info("Preview button click")
        if self.url_input.get() != "":
            self.browser_frame.update_url(self.url_input.get())
        else:
            logging.info("Ignoring preview button click due to empty input")
        # return "break"

    def custom_artist_fn(self):
        # TODO: Can add popup box or something here for user to confirm artist name
        return ""


class BrowserFrame(tkinter.Frame):
    def __init__(self, master, cnf={}, **kw):
        self.closing = False
        self.browser = None
        tkinter.Frame.__init__(self, master, cnf, **kw)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

#"https://soundcloud.com/cryingelf/ayw-its-a-bonfire"

    def update_url(self, url):
        self.browser.StopLoad()
        self.browser.LoadUrl(url)

    def embed_browser(self):
        self.window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        self.window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(self.window_info, url="https://soundcloud.com/cryingelf/ayw-its-a-bonfire")
        assert self.browser
        self.message_loop_work()

    def get_window_handle(self):
        return self.winfo_id()

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        ctypes.windll.user32.SetWindowPos(self.browser.GetWindowHandle(), 0, 0, 0, width, height, 0x0002)
        self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    def clear_browser_references(self):
        self.browser = None
