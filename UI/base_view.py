import ttkbootstrap as tb
from ttkbootstrap.constants import *


class BaseView(tb.Frame):

    def __init__(self, master, title):

        super().__init__(master)

        tb.Label(
            self,
            text=title,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.body = tb.Frame(self)
        self.body.pack(fill=BOTH, expand=True, padx=20, pady=10)