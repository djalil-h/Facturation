import ttkbootstrap as tb
from ttkbootstrap.constants import *


class StatCard(tb.Frame):

    def __init__(
        self,
        master,
        title,
        value,
        icon="📊",
        color="primary"
    ):

        super().__init__(
            master,
            bootstyle="light",
            padding=15
        )

        self.configure(borderwidth=1)

        self.columnconfigure(1, weight=1)

        # Icône
        tb.Label(
            self,
            text=icon,
            font=("Segoe UI Emoji", 28)
        ).grid(row=0, column=0, rowspan=2, padx=10)

        # Titre
        tb.Label(
            self,
            text=title,
            font=("Segoe UI", 10),
            foreground="#6B7280"
        ).grid(row=0, column=1, sticky="w")

        # Valeur
        self.lbl_value = tb.Label(
            self,
            text=value,
            font=("Segoe UI", 20, "bold"),
            bootstyle=color
        )

        self.lbl_value.grid(row=1, column=1, sticky="w")

    def set_value(self, value):

        self.lbl_value.configure(text=value)