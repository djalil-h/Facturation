import ttkbootstrap as tb
from ttkbootstrap.constants import *


class SearchBar(tb.Frame):

    def __init__(self, master, command=None):

        super().__init__(master)

        self.command = command

        self.columnconfigure(0, weight=1)

        self.entry = tb.Entry(
            self,
            font=("Segoe UI", 11)
        )

        self.entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10)
        )

        self.entry.bind("<KeyRelease>", self.search)

        tb.Button(
            self,
            text="Rechercher",
            bootstyle="primary",
            command=self.search
        ).grid(
            row=0,
            column=1
        )

    def search(self, event=None):

        if self.command:

            self.command(
                self.entry.get()
            )