import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.base_view import BaseView


class UtilisateursView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Utilisateurs")

        tb.Label(
            self.body,
            text="Gestion des utilisateurs",
            font=("Segoe UI", 12)
        ).pack(anchor="w")