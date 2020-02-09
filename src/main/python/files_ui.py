import tkinter
import os
from tkinter import ttk
from definitions import DATA_PATH

class FilesUI:
    def __init__(self, parent):
        self.container = tkinter.Frame(parent)
        self.directory_frame = tkinter.Frame(self.container)
        self.directory_tree_label = tkinter.Label(self.directory_frame, text="Files")
        self.directory_tree = ttk.Treeview(self.directory_frame)
        self.directory_tree_root = self.directory_tree.insert('', 'end', 'root', text="Downloads")
        self.directory_tree_scroll = ttk.Scrollbar(self.directory_frame, orient="vertical", command=self.directory_tree.yview)
        self.directory_tree.configure(yscrollcommand=self.directory_tree_scroll.set)
        self.layout()
        self.build_directory_tree()

    def layout(self):
        self.container.pack(expand="yes",fill="both")
        self.container.columnconfigure(0, weight=1, uniform="col0")
        self.container.rowconfigure(0, weight=1, uniform="row0")
        self.container.rowconfigure(1, weight=1, uniform="row0")

        self.directory_frame.grid(row=0, column=0, sticky="nsew")
        self.directory_frame.columnconfigure(0, weight=9, uniform="col0")
        self.directory_frame.columnconfigure(1, weight=0, uniform="col0")
        self.directory_frame.rowconfigure(0, weight=1, uniform="row0")
        self.directory_frame.rowconfigure(1, weight=12, uniform="row0")
        self.directory_tree_label.grid(row=0, column=0, sticky="nsw")
        self.directory_tree.grid(row=1, column=0, sticky="nsew")
        self.directory_tree_scroll.grid(row=1, column=1, sticky="nse")

    def build_directory_tree(self):
        # root = self.directory_tree.get_children()
        # to_delete = list(filter(lambda x: x != 'root', self.directory_tree.get_children()))
        # self.directory_tree.delete(to_delete)
        self.build_directory_tree_iter(DATA_PATH, self.directory_tree_root)

    def build_directory_tree_iter(self, path, parent):
        for next in os.listdir(path):
            next_path = os.path.join(path, next)
            next_parent = self.directory_tree.insert(parent, 'end', text=next)
            if os.path.isdir(next_path):
                self.build_directory_tree_iter(next_path, next_parent)