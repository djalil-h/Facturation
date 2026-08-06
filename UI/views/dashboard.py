import ttkbootstrap as tb
from ttkbootstrap.constants import *

from services.dashboard_service import statistiques_generales


class Dashboard(tb.Frame):

    def __init__(self, master):

        super().__init__(master)

        self.build()

    def build(self):

        stats = statistiques_generales()

        tb.Label(

            self,

            text="TABLEAU DE BORD",

            font=("Segoe UI", 24, "bold")

        ).pack(anchor=W, padx=25, pady=20)

        cards = tb.Frame(self)

        cards.pack(fill=X, padx=20)

        self.card(cards, "Factures", stats["total_factures"])

        self.card(cards, "Montant", f"{stats['montant_total']:,.2f} DA")

        self.card(cards, "Payé", f"{stats['montant_paye']:,.2f} DA")

        self.card(cards, "Reste", f"{stats['reste']:,.2f} DA")

    def card(self, parent, titre, valeur):

        frame = tb.Frame(parent, padding=15)

        frame.pack(side=LEFT, padx=10)

        tb.Label(

            frame,

            text=titre,

            font=("Segoe UI", 12)

        ).pack()

        tb.Label(

            frame,

            text=valeur,

            font=("Segoe UI", 18, "bold")

        ).pack()