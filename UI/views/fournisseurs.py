import ttkbootstrap as tb

from UI.base_view import BaseView


class FournisseursView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Gestion des fournisseurs")

        tb.Label(
            self.body,
            text="Liste des fournisseurs"
        ).pack()