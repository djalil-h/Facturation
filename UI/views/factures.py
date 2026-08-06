import ttkbootstrap as tb

from UI.base_view import BaseView


class FacturesView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Gestion des factures")

        tb.Label(
            self.body,
            text="Liste des factures"
        ).pack()