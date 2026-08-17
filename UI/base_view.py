import ttkbootstrap as tb
from ttkbootstrap.constants import *


class BaseView(tb.Frame):
    """Socle visuel commun à toutes les pages, avec une typographie accessible."""

    def __init__(self, master, title):
        super().__init__(master, bootstyle="light", padding=(6, 6, 6, 0))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tb.Frame(self, bootstyle="light", padding=(10, 10, 10, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tb.Label(
            header,
            text=title,
            font=("Segoe UI", 21, "bold"),
            bootstyle="dark",
        ).grid(row=0, column=0, sticky="w")

        self.body = tb.Frame(self, bootstyle="light")
        self.body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)
