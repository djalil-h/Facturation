import ttkbootstrap as tb
from ttkbootstrap.constants import *


class BaseView(tb.Frame):
    """Socle visuel commun à toutes les pages."""

    def __init__(self, master, title):
        super().__init__(master, bootstyle="light", padding=(4, 4, 4, 0))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tb.Frame(self, bootstyle="light", padding=(8, 8, 8, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tb.Label(
            header,
            text=title,
            font=("Segoe UI", 18, "bold"),
            bootstyle="dark",
        ).grid(row=0, column=0, sticky="w")

        self.body = tb.Frame(self, bootstyle="light")
        self.body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 6))
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)
