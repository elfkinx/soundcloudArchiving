import tkinter
from tkinter import messagebox
from cefpython3 import cefpython as cef
import ctypes
import logging
import main.python.scdownload as scdownload

"""
scdownload (SoundCloud Downloader)

This file defines the left-hand side of the GUI concerned with:
- specifying the soundcloud track URL in order to preview or download
- displaying a HTML rendered preview of the soundcloud track page (using cef)
- toggling different pieces of metadata to download about the track, artist, or playlist/album

"""

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

        ####################### TRACK METADATA #######################################

        self.track_metadata_frame = tkinter.Frame(self.metadata_frame)

        self.track_title_label = tkinter.Label(self.track_metadata_frame, text="Track")

        self.track_albums_button = tkinter.Button(self.track_metadata_frame, text="Albums")
        self.track_artist_button = tkinter.Button(self.track_metadata_frame, text="Artist")
        self.track_background_button = tkinter.Button(self.track_metadata_frame, text="Background")
        self.track_comments_button = tkinter.Button(self.track_metadata_frame, text="Comments")
        self.track_cover_art_button = tkinter.Button(self.track_metadata_frame, text="Cover Art")
        self.track_date_button = tkinter.Button(self.track_metadata_frame, text="Date")
        self.track_description_button = tkinter.Button(self.track_metadata_frame, text="Description")
        self.track_likes_button = tkinter.Button(self.track_metadata_frame, text="Likes")
        self.track_listens_button = tkinter.Button(self.track_metadata_frame, text="Listens")
        self.track_playlists_button = tkinter.Button(self.track_metadata_frame, text="Playlists")
        self.track_related_tracks_button = tkinter.Button(self.track_metadata_frame, text="Related Tracks")
        self.track_reposts_button = tkinter.Button(self.track_metadata_frame, text="Reposts")
        self.track_status_button = tkinter.Button(self.track_metadata_frame, text="Status")
        self.track_tags_button = tkinter.Button(self.track_metadata_frame, text="Tags")

        self.selected_track_metadata = set()

        ######################## ARTIST METADATA #####################################

        self.artist_metadata_frame = tkinter.Frame(self.metadata_frame)

        self.artist_title_label = tkinter.Label(self.artist_metadata_frame, text="Artist")

        self.artist_albums_button = tkinter.Button(self.artist_metadata_frame, text="Albums")
        self.artist_comments_button = tkinter.Button(self.artist_metadata_frame, text="Comments")
        self.artist_description_button = tkinter.Button(self.artist_metadata_frame, text="Description")
        self.artist_location_button = tkinter.Button(self.artist_metadata_frame, text="Location")
        self.artist_name_button = tkinter.Button(self.artist_metadata_frame, text="Name")
        self.artist_username_button = tkinter.Button(self.artist_metadata_frame, text="Username")
        self.artist_followers_button = tkinter.Button(self.artist_metadata_frame, text="Followers")
        self.artist_following_button = tkinter.Button(self.artist_metadata_frame, text="Following")
        self.artist_likes_button = tkinter.Button(self.artist_metadata_frame, text="Likes")
        self.artist_reposts_button = tkinter.Button(self.artist_metadata_frame, text="Reposts")
        self.artist_user_id_button = tkinter.Button(self.artist_metadata_frame, text="User ID")
        self.artist_status_button = tkinter.Button(self.artist_metadata_frame, text="Status")
        self.artist_profile_picture_button = tkinter.Button(self.artist_metadata_frame, text="Profile Picture")
        self.artist_header_button = tkinter.Button(self.artist_metadata_frame, text="Header")
        self.artist_links_button = tkinter.Button(self.artist_metadata_frame, text="Links")
        self.artist_playlists_button = tkinter.Button(self.artist_metadata_frame, text="Playlists")
        self.artist_spotlight_button = tkinter.Button(self.artist_metadata_frame, text="Spotlight")

        self.selected_artist_metadata = set()

        ########################## PLAYLIST METADATA #################################

        self.playlist_metadata_frame = tkinter.Frame(self.metadata_frame)

        self.playlist_title_label = tkinter.Label(self.playlist_metadata_frame, text="Playlist/Album")

        self.playlist_artist_button = tkinter.Button(self.playlist_metadata_frame, text="Artist")
        self.playlist_cover_art_button = tkinter.Button(self.playlist_metadata_frame, text="Cover Art")
        self.playlist_date_button = tkinter.Button(self.playlist_metadata_frame, text="Date")
        self.playlist_description_button = tkinter.Button(self.playlist_metadata_frame, text="Description")
        self.playlist_length_button = tkinter.Button(self.playlist_metadata_frame, text="Length")
        self.playlist_likes_button = tkinter.Button(self.playlist_metadata_frame, text="Likes")
        self.playlist_reposts_button = tkinter.Button(self.playlist_metadata_frame, text="Reposts")
        self.playlist_tags_button = tkinter.Button(self.playlist_metadata_frame, text="Tags")
        self.playlist_tracks_button = tkinter.Button(self.playlist_metadata_frame, text="Tracks")

        self.selected_playlist_metadata = set()

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
        self.track_metadata_frame.rowconfigure(0, weight=1, uniform="row0")
        self.track_metadata_frame.rowconfigure(1, weight=1, uniform="row0")
        self.track_metadata_frame.rowconfigure(2, weight=1, uniform="row0")
        self.track_metadata_frame.columnconfigure(0, weight=1, uniform="col0")
        self.track_metadata_frame.columnconfigure(1, weight=1, uniform="col0")
        self.track_metadata_frame.columnconfigure(2, weight=1, uniform="col0")
        self.track_metadata_frame.columnconfigure(3, weight=1, uniform="col0")
        self.track_metadata_frame.columnconfigure(4, weight=1, uniform="col0")
        self.track_metadata_frame.columnconfigure(5, weight=1, uniform="col0")
        self.track_metadata_frame.columnconfigure(6, weight=1, uniform="col0")

        self.track_title_label.grid(row=0, column=0, sticky="w")

        xpad = 3
        self.track_albums_button.grid(row=1, column=0, sticky="ew", padx=xpad)
        self.track_artist_button.grid(row=1, column=1, sticky="ew", padx=xpad)
        self.track_background_button.grid(row=1, column=2, sticky="ew", padx=xpad)
        self.track_comments_button.grid(row=1, column=3, sticky="ew", padx=xpad)
        self.track_cover_art_button.grid(row=1, column=4, sticky="ew", padx=xpad)
        self.track_date_button.grid(row=1, column=5, sticky="ew", padx=xpad)
        self.track_description_button.grid(row=1, column=6, sticky="ew", padx=xpad)

        self.track_likes_button.grid(row=2, column=0, sticky="ew", padx=xpad)
        self.track_listens_button.grid(row=2, column=1, sticky="ew", padx=xpad)
        self.track_playlists_button.grid(row=2, column=2, sticky="ew", padx=xpad)
        self.track_related_tracks_button.grid(row=2, column=3, sticky="ew", padx=xpad)
        self.track_reposts_button.grid(row=2, column=4, sticky="ew", padx=xpad)
        self.track_status_button.grid(row=2, column=5, sticky="ew", padx=xpad)
        self.track_tags_button.grid(row=2, column=6, sticky="ew", padx=xpad)

        self.artist_title_label.grid(row=0, column=0, sticky="w")

        self.artist_metadata_frame.grid(row=1, column=0, sticky="nsew")
        self.artist_metadata_frame.rowconfigure(0, weight=1, uniform="row0")
        self.artist_metadata_frame.rowconfigure(1, weight=1, uniform="row0")
        self.artist_metadata_frame.rowconfigure(2, weight=1, uniform="row0")
        self.artist_metadata_frame.rowconfigure(3, weight=1, uniform="row0")
        self.artist_metadata_frame.columnconfigure(0, weight=1, uniform="col0")
        self.artist_metadata_frame.columnconfigure(1, weight=1, uniform="col0")
        self.artist_metadata_frame.columnconfigure(2, weight=1, uniform="col0")
        self.artist_metadata_frame.columnconfigure(3, weight=1, uniform="col0")
        self.artist_metadata_frame.columnconfigure(4, weight=1, uniform="col0")
        self.artist_metadata_frame.columnconfigure(5, weight=1, uniform="col0")
        self.artist_metadata_frame.columnconfigure(6, weight=1, uniform="col0")

        self.artist_albums_button.grid(row=1, column=0, sticky="ew", padx=xpad)
        self.artist_comments_button.grid(row=1, column=1, sticky="ew", padx=xpad)
        self.artist_description_button.grid(row=1, column=2, sticky="ew", padx=xpad)
        self.artist_location_button.grid(row=1, column=3, sticky="ew", padx=xpad)
        self.artist_name_button.grid(row=1, column=4, sticky="ew", padx=xpad)
        self.artist_username_button.grid(row=1, column=5, sticky="ew", padx=xpad)
        self.artist_following_button.grid(row=1, column=6, sticky="ew", padx=xpad)

        self.artist_likes_button.grid(row=2, column=0, sticky="ew", padx=xpad)
        self.artist_reposts_button.grid(row=2, column=1, sticky="ew", padx=xpad)
        self.artist_user_id_button.grid(row=2, column=2, sticky="ew", padx=xpad)
        self.artist_status_button.grid(row=2, column=3, sticky="ew", padx=xpad)
        self.artist_profile_picture_button.grid(row=2, column=4, sticky="ew", padx=xpad)
        self.artist_header_button.grid(row=2, column=5, sticky="ew", padx=xpad)
        self.artist_links_button.grid(row=2, column=6, sticky="ew", padx=xpad)

        self.artist_playlists_button.grid(row=3, column=0, sticky="ew", padx=xpad)
        self.artist_spotlight_button.grid(row=3, column=1, sticky="ew", padx=xpad)

        self.playlist_metadata_frame.grid(row=2, column=0, sticky="nsew")
        self.playlist_metadata_frame.rowconfigure(0, weight=1, uniform="row0")
        self.playlist_metadata_frame.rowconfigure(1, weight=1, uniform="row0")
        self.playlist_metadata_frame.rowconfigure(2, weight=1, uniform="row0")
        self.playlist_metadata_frame.columnconfigure(0, weight=1, uniform="col0")
        self.playlist_metadata_frame.columnconfigure(1, weight=1, uniform="col0")
        self.playlist_metadata_frame.columnconfigure(2, weight=1, uniform="col0")
        self.playlist_metadata_frame.columnconfigure(3, weight=1, uniform="col0")
        self.playlist_metadata_frame.columnconfigure(4, weight=1, uniform="col0")
        self.playlist_metadata_frame.columnconfigure(5, weight=1, uniform="col0")
        self.playlist_metadata_frame.columnconfigure(6, weight=1, uniform="col0")

        self.playlist_title_label.grid(row=0, column=0, sticky="w")

        self.playlist_artist_button.grid(row=1, column=0, stick="ew", padx=xpad)
        self.playlist_cover_art_button.grid(row=1, column=1, stick="ew", padx=xpad)
        self.playlist_date_button.grid(row=1, column=2, stick="ew", padx=xpad)
        self.playlist_description_button.grid(row=1, column=3, stick="ew", padx=xpad)
        self.playlist_length_button.grid(row=1, column=4, stick="ew", padx=xpad)
        self.playlist_likes_button.grid(row=1, column=5, stick="ew", padx=xpad)
        self.playlist_reposts_button.grid(row=1, column=6, stick="ew", padx=xpad)

        self.playlist_tags_button.grid(row=2, column=0, stick="ew", padx=xpad)
        self.playlist_tracks_button.grid(row=2, column=1, stick="ew", padx=xpad)


    def bind_handlers(self):
        self.download_button.bind("<Button-1>", self.download_button_click)
        self.preview_button.bind("<Button-1>", self.preview_button_click)
        self.url_input.bind("<Button-1>", self.force_focus)

        self.track_albums_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_artist_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_background_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_comments_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_cover_art_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_date_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_description_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_likes_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_listens_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_playlists_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_related_tracks_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_reposts_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_status_button.bind("<Button-1>", self.track_tag_button_handler)
        self.track_tags_button.bind("<Button-1>", self.track_tag_button_handler)

        self.artist_albums_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_comments_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_description_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_location_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_name_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_username_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_followers_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_following_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_likes_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_reposts_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_user_id_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_status_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_profile_picture_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_header_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_links_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_playlists_button.bind("<Button-1>", self.artist_tag_button_handler)
        self.artist_spotlight_button.bind("<Button-1>", self.artist_tag_button_handler)

        self.playlist_artist_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_cover_art_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_date_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_description_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_length_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_likes_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_reposts_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_tags_button.bind("<Button-1>", self.playlist_tag_button_handler)
        self.playlist_tracks_button.bind("<Button-1>", self.playlist_tag_button_handler)

    def track_tag_button_handler(self, event):
        self.tag_button_handler(event, self.selected_track_metadata)

    def artist_tag_button_handler(self, event):
        self.tag_button_handler(event, self.selected_artist_metadata)

    def playlist_tag_button_handler(self, event):
        self.tag_button_handler(event, self.selected_playlist_metadata)

    # We toggle the colour of the button after it has been pressed and add the corresponding metadata key to the given
    # metadata_store set in order to download the correct metadata when requested
    def tag_button_handler(self, event, metadata_store):
        metadata_clicked = self.button_name_to_key(event.widget['text'])
        if event.widget['bg'] == "#48cbd4":
            logging.info("De-selecting metadata: " + metadata_clicked)
            metadata_store.remove(metadata_clicked)
            event.widget.configure(bg="#FFF", fg="#000")
        else:
            logging.info("Selecting metadata: " + metadata_clicked)
            metadata_store.add(metadata_clicked)
            event.widget.configure(bg="#48cbd4", fg="#FFF")

    def button_name_to_key(self, name):
        return name.lower().replace(" ", "_")

    def force_focus(self, event):
        event.widget.focus_force()

    def download_button_click(self, event):
        logging.info("Download button click")
        if self.url_input.get() != "":
            # An important improvement to the app would be to make the download functionality asynchronous so that it
            # doesn't block the UI (especially when downloading e.g. large playlists)
            logging.info("Downloading with track metadata: " + str(self.selected_track_metadata))
            logging.info("Downloading with artist metadata: " + str(self.selected_artist_metadata))
            logging.info("Downloading with playlist metadata: " + str(self.selected_playlist_metadata))
            result = scdownload.download(self.url_input.get(), self.custom_artist_fn, self.selected_track_metadata,
                                         self.selected_artist_metadata, self.selected_playlist_metadata)
            messagebox.showinfo("Alert", "Downloaded with result: " + str(result))
        else:
            logging.info("Ignoring download click due to empty input")

    def preview_button_click(self, event):
        logging.info("Preview button click")
        if self.url_input.get() != "":
            self.browser_frame.update_url(self.url_input.get())
        else:
            logging.info("Ignoring preview button click due to empty input")
        # return "break"

    def custom_artist_fn(self):
        # This would be a place to add a custom pop-up (or other functionality) in order to determine what the correct
        # artist name is for a download. This isn't possible to determine from the soundcloud information, and at the
        # moment it defaults to the username of the user who uploaded the track.
        # This is called back during the download process
        return ""

# The code below displays a preview of the webpage using the cef module
# This is adapted from the cefpython examples for tkinter:
#   https://github.com/cztomczak/cefpython/blob/master/examples/tkinter_.py#L148
class BrowserFrame(tkinter.Frame):
    def __init__(self, master, cnf={}, **kw):
        self.closing = False
        self.browser = None
        tkinter.Frame.__init__(self, master, cnf, **kw)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    # This is where we update the preview when the button is clicked by the user
    def update_url(self, url):
        self.browser.StopLoad()
        self.browser.LoadUrl(url)

    def embed_browser(self):
        self.window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        self.window_info.SetAsChild(self.get_window_handle(), rect)
        # The URL below is used as a default in order to demonstrate the preview functionality
        self.browser = cef.CreateBrowserSync(self.window_info, url="https://soundcloud.com/cryingelf/ayw-its-a-bonfire")
        assert self.browser
        self.message_loop_work()

    def get_window_handle(self):
        return self.winfo_id()

    # This responds to user input by checking in a busy loop (every 10ms) for changes
    # This is sub-optimal and can lead to excessive CPU consumption. An alternative solution would be to use the async
    # CEF api but this hasn't been ported to pythong yet and would likely require significant additions to the cef
    # python wrapper
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
