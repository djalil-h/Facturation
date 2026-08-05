import ttkbootstrap as tb
from ttkbootstrap.constants import *


class Sidebar(tb.Frame):

    def __init__(self, master):

        super().__init__(master, width=250)

        self.pack_propagate(False)

        self.build()

    def build(self):

        tb.Label(

            self,

            text="⚕ HH",

            font=("Segoe UI", 22, "bold")

        ).pack(pady=25)

        tb.Label(

            self,

            text="Facturation",

            font=("Segoe UI", 14, "bold")

        ).pack()

        tb.Label(

            self,

            text="Pharmacie Hamzaoui Hamid",

            font=("Segoe UI", 9)

        ).pack(pady=(0, 30))

        menus = [

            "🏠 Tableau de bord",

            "📦 Fournisseurs",

            "🧾 Factures",

            "💳 Paiements",

            "📊 Statistiques",

            "📜 Historique",

            "👤 Utilisateurs",

            "🛡 Journal",

            "⚙ Paramètres"

        ]

        for menu in menus:

            tb.Button(

                self,

                text=menu,

                bootstyle="secondary-outline",

                width=25

            ).pack(pady=4, padx=10)