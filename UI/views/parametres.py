import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.base_view import BaseView


class ParametresView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Paramètres")

        tb.Label(
            self.body,
            text="Configuration de l'application",
            font=("Segoe UI", 12)
        ).pack(anchor="w")