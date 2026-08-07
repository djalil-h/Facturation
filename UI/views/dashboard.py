import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk

from UI.base_view import BaseView

from UI.widgets.stat_card import StatCard
from UI.widgets.search_bar import SearchBar
from UI.widgets.modern_table import ModernTable

from services.dashboard_service import DashboardService


class Dashboard(BaseView):

    def __init__(self, master):

        super().__init__(master)

        self.data = {}

        self.build()

        self.refresh_dashboard()

    # ============================================================
    # CONSTRUCTION
    # ============================================================

    def build(self):

        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(0, weight=1)

        # ---------------------------------------------------
        # TITRE
        # ---------------------------------------------------

        tb.Label(

            self,

            text="TABLEAU DE BORD",

            font=("Segoe UI", 22, "bold")

        ).pack(

            anchor="w",

            padx=20,

            pady=(20, 10)

        )

        # ---------------------------------------------------
        # CARTES
        # ---------------------------------------------------

        cards = tb.Frame(self)

        cards.pack(

            fill=X,

            padx=20,

            pady=10

        )

        for i in range(6):

            cards.columnconfigure(i, weight=1)

        self.card_factures = StatCard(

            cards,

            "Factures",

            "0",

            "📄",

            "primary"

        )

        self.card_factures.grid(

            row=0,

            column=0,

            padx=5,

            sticky="nsew"

        )

        self.card_total = StatCard(

            cards,

            "Montant Total",

            "0 DA",

            "💰",

            "success"

        )

        self.card_total.grid(

            row=0,

            column=1,

            padx=5,

            sticky="nsew"

        )

        self.card_paye = StatCard(

            cards,

            "Montant Payé",

            "0 DA",

            "✅",

            "info"

        )

        self.card_paye.grid(

            row=0,

            column=2,

            padx=5,

            sticky="nsew"

        )

        self.card_reste = StatCard(

            cards,

            "Reste",

            "0 DA",

            "⌛",

            "warning"

        )

        self.card_reste.grid(

            row=0,

            column=3,

            padx=5,

            sticky="nsew"

        )

        self.card_retard = StatCard(

            cards,

            "Retard",

            "0",

            "🔴",

            "danger"

        )

        self.card_retard.grid(

            row=0,

            column=4,

            padx=5,

            sticky="nsew"

        )

        self.card_echeance = StatCard(

            cards,

            "Échéances",

            "0",

            "📅",

            "secondary"

        )

        self.card_echeance.grid(

            row=0,

            column=5,

            padx=5,

            sticky="nsew"

        )

        # ---------------------------------------------------
        # RECHERCHE
        # ---------------------------------------------------

        self.search = SearchBar(

            self,

            command=self.search_facture

        )

        self.search.pack(

            fill=X,

            padx=20,

            pady=15

        )

        # ---------------------------------------------------
        # CONTENU
        # ---------------------------------------------------

        content = tb.Frame(self)

        content.pack(

            fill=BOTH,

            expand=True,

            padx=20,

            pady=10

        )

        content.columnconfigure(0, weight=3)

        content.columnconfigure(1, weight=1)

        content.rowconfigure(0, weight=1)

        self.left_panel = tb.Frame(content)

        self.left_panel.grid(

            row=0,

            column=0,

            sticky="nsew",

            padx=(0, 10)

        )

        self.right_panel = tb.Frame(content)

        self.right_panel.grid(

            row=0,

            column=1,

            sticky="nsew"

        )
        self.build_panels()
    # ============================================================
    # TABLEAU DES DERNIÈRES FACTURES
    # ============================================================

    def build_latest_invoices(self):

        title = tb.Label(
            self.left_panel,
            text="Dernières factures",
            font=("Segoe UI", 15, "bold")
        )

        title.pack(
            anchor="w",
            pady=(0, 10)
        )

        table_frame = tb.Frame(self.left_panel)

        table_frame.pack(
            fill=BOTH,
            expand=True
        )

        columns = (
            "ID",
            "Numéro",
            "Fournisseur",
            "Date",
            "Échéance",
            "Montant",
            "Statut"
        )

        self.invoice_table = ModernTable(
            table_frame,
            columns
        )

        self.invoice_table.pack(
            fill=BOTH,
            expand=True
        )

    # ============================================================
    # PANNEAU NOTIFICATIONS
    # ============================================================

    def build_notifications(self):

        frame = tb.Labelframe(
            self.right_panel,
            text="🔔 Notifications",
            padding=12
        )

        frame.pack(
            fill=X,
            pady=(0, 15)
        )

        self.notification_frame = tb.Frame(frame)

        self.notification_frame.pack(
            fill=X
        )

    # ============================================================
    # PANNEAU ÉCHÉANCES
    # ============================================================

    def build_due(self):

        frame = tb.Labelframe(
            self.right_panel,
            text="⏰ Échéances",
            padding=12
        )

        frame.pack(
            fill=BOTH,
            expand=True
        )

        self.due_frame = tb.Frame(frame)

        self.due_frame.pack(
            fill=BOTH,
            expand=True
        )

    # ============================================================
    # CONSTRUCTION DES PANNEAUX
    # ============================================================

    def build_panels(self):

        self.build_latest_invoices()

        self.build_notifications()

        self.build_due()

    # ============================================================
    # ACTUALISATION DES NOTIFICATIONS
    # ============================================================

    def refresh_notifications(self):

        for widget in self.notification_frame.winfo_children():

            widget.destroy()

        notifications = self.data.get(
            "notifications",
            []
        )

        if not notifications:

            tb.Label(
                self.notification_frame,
                text="✓ Aucune notification",
                bootstyle="success"
            ).pack(
                anchor="w",
                pady=5
            )

            return

        for notification in notifications:

            tb.Label(
                self.notification_frame,
                text=f"• {notification}",
                wraplength=300,
                justify="left"
            ).pack(
                anchor="w",
                pady=5
            )

    # ============================================================
    # ACTUALISATION DES ÉCHÉANCES
    # ============================================================

    def refresh_due(self):

        for widget in self.due_frame.winfo_children():

            widget.destroy()

        factures = self.data.get(
            "dernieres",
            []
        )

        if not factures:

            tb.Label(
                self.due_frame,
                text="Aucune facture",
                bootstyle="secondary"
            ).pack(
                anchor="w",
                pady=5
            )

            return

        compteur = 0

        for facture in factures:

            statut = getattr(
                facture,
                "statut",
                ""
            )

            if str(statut).lower() == "payée":

                continue

            date_echeance = getattr(
                facture,
                "date_echeance",
                ""
            )

            numero = getattr(
                facture,
                "numero",
                getattr(
                    facture,
                    "numero_facture",
                    facture.id
                )
            )

            montant = getattr(
                facture,
                "montant",
                0
            )

            texte = (
                f"{numero}\n"
                f"Échéance : {date_echeance}\n"
                f"Montant : {montant:,.2f} DA"
            )

            item = tb.Frame(
                self.due_frame,
                padding=8
            )

            item.pack(
                fill=X,
                pady=4
            )

            tb.Label(
                item,
                text=texte,
                justify="left",
                font=("Segoe UI", 9)
            ).pack(
                anchor="w"
            )

            compteur += 1

            if compteur >= 5:

                break

        if compteur == 0:

            tb.Label(
                self.due_frame,
                text="✓ Aucune échéance en attente",
                bootstyle="success"
            ).pack(
                anchor="w",
                pady=5
            )
    # ============================================================
    # ACTUALISATION DU DASHBOARD
    # ============================================================

    def refresh_dashboard(self):

        try:

            self.data = DashboardService.get_dashboard_data()

            self.refresh_cards()
            self.refresh_latest_invoices()
            self.refresh_notifications()
            self.refresh_due()

        except Exception as e:

            print("Erreur Dashboard :", e)

    # ============================================================
    # ACTUALISATION DES CARTES
    # ============================================================

    def refresh_cards(self):

        total_factures = self.data.get(
            "total_factures",
            0
        )

        montant_total = self.data.get(
            "montant_total",
            0
        )

        montant_paye = self.data.get(
            "montant_paye",
            0
        )

        reste = self.data.get(
            "reste",
            0
        )

        retard = self.data.get(
            "retard",
            0
        )

        echeance = self.data.get(
            "echeance",
            0
        )

        self.card_factures.set_value(
            str(total_factures)
        )

        self.card_total.set_value(
            self.format_amount(montant_total)
        )

        self.card_paye.set_value(
            self.format_amount(montant_paye)
        )

        self.card_reste.set_value(
            self.format_amount(reste)
        )

        self.card_retard.set_value(
            str(retard)
        )

        self.card_echeance.set_value(
            str(echeance)
        )

    # ============================================================
    # FORMAT MONÉTAIRE
    # ============================================================

    @staticmethod
    def format_amount(amount):

        try:

            amount = float(amount)

        except (TypeError, ValueError):

            amount = 0

        return f"{amount:,.2f} DA"

    # ============================================================
    # ACTUALISATION DU TABLEAU
    # ============================================================

    def refresh_latest_invoices(self):

        if not hasattr(
            self,
            "invoice_table"
        ):
            return

        rows = []

        for facture in self.data.get(
            "dernieres",
            []
        ):

            numero = getattr(
                facture,
                "numero",
                getattr(
                    facture,
                    "numero_facture",
                    facture.id
                )
            )

            fournisseur = getattr(
                facture,
                "fournisseur",
                None
            )

            if fournisseur:

                fournisseur_nom = getattr(
                    fournisseur,
                    "nom",
                    str(fournisseur)
                )

            else:

                fournisseur_nom = (
                    getattr(
                        facture,
                        "fournisseur_id",
                        ""
                    )
                )

            date_facture = getattr(
                facture,
                "date_facture",
                ""
            )

            date_echeance = getattr(
                facture,
                "date_echeance",
                ""
            )

            montant = getattr(
                facture,
                "montant",
                0
            )

            statut = getattr(
                facture,
                "statut",
                ""
            )

            rows.append(
                (
                    facture.id,
                    numero,
                    fournisseur_nom,
                    date_facture,
                    date_echeance,
                    self.format_amount(montant),
                    statut
                )
            )

        self.invoice_table.load_data(rows)

        self.invoice_table.autosize()

    # ============================================================
    # RECHERCHE RAPIDE
    # ============================================================

    def search_facture(self, texte):

        texte = str(
            texte
        ).strip().lower()

        if not hasattr(
            self,
            "invoice_table"
        ):
            return

        if not texte:

            self.refresh_latest_invoices()

            return

        resultats = []

        for facture in self.data.get(
            "dernieres",
            []
        ):

            numero = str(
                getattr(
                    facture,
                    "numero",
                    getattr(
                        facture,
                        "numero_facture",
                        ""
                    )
                )
            )

            statut = str(
                getattr(
                    facture,
                    "statut",
                    ""
                )
            )

            fournisseur = getattr(
                facture,
                "fournisseur",
                None
            )

            fournisseur_nom = ""

            if fournisseur:

                fournisseur_nom = str(
                    getattr(
                        fournisseur,
                        "nom",
                        ""
                    )
                )

            if (
                texte in numero.lower()
                or texte in statut.lower()
                or texte in fournisseur_nom.lower()
            ):

                montant = getattr(
                    facture,
                    "montant",
                    0
                )

                resultats.append(
                    (
                        facture.id,
                        numero,
                        fournisseur_nom,
                        getattr(
                            facture,
                            "date_facture",
                            ""
                        ),
                        getattr(
                            facture,
                            "date_echeance",
                            ""
                        ),
                        self.format_amount(
                            montant
                        ),
                        statut
                    )
                )

        self.invoice_table.load_data(
            resultats
        )

        self.invoice_table.autosize()