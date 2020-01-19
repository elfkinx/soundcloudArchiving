import tkinter
import os
from tkinter import ttk
from definitions import DATA_PATH

class FilesUI:
    def __init__(self, parent):
        self.directory_tree = ttk.Treeview(parent)
        self.ent = tkinter.Entry(parent,takefocus=True)
        self.layout()
        self.build_directory_tree()

    def layout(self):
        self.ent.pack(expand="yes",fill="both")
        self.directory_tree.pack(expand='yes',fill='both')

    def build_directory_tree(self):
        root = self.directory_tree.insert('', 'end', 'root', text="Downloads")
        self.build_directory_tree_iter(DATA_PATH, root)

    def build_directory_tree_iter(self, path, parent):
        for next in os.listdir(path):
            next_path = os.path.join(path, next)
            next_parent = self.directory_tree.insert(parent, 'end', text=next)
            if os.path.isdir(next_path):
                self.build_directory_tree_iter(next_path, next_parent)