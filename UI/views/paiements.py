import ttkbootstrap as tb

from UI.base_view import BaseView


class PaiementsView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Gestion des paiements")

        tb.Label(
            self.body,
            text="Liste des paiements"
        ).pack()