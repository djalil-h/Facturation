import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.base_view import BaseView


class HistoriqueView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Historique")

        tb.Label(
            self.body,
            text="Historique des opérations",
            font=("Segoe UI", 12)
        ).pack(anchor="w")