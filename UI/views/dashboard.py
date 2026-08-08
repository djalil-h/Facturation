import tkinter as tk
from tkinter import ttk
from datetime import date

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.base_view import BaseView
from UI.widgets.stat_card import StatCard
from UI.widgets.search_bar import SearchBar
from services.dashboard_service import DashboardService


class Dashboard(BaseView):
    """Dashboard orienté trésorerie et dettes fournisseurs."""

    def __init__(self, master):
        super().__init__(master, "Tableau de bord")
        self.data = {}
        self.build()
        self.refresh_dashboard()

    def build(self):
        self.pack(fill=BOTH, expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        cards = tb.Frame(self)
        cards.pack(fill=X, padx=20, pady=(10, 15))
        for i in range(6):
            cards.columnconfigure(i, weight=1)

        self.card_factures = StatCard(cards, "Factures", "0", "📄", "primary")
        self.card_factures.grid(row=0, column=0, padx=5, sticky="nsew")
        self.card_dette = StatCard(cards, "Dette fournisseurs", "0 DA", "💳", "danger")
        self.card_dette.grid(row=0, column=1, padx=5, sticky="nsew")
        self.card_paye = StatCard(cards, "Montant Payé", "0 DA", "✅", "success")
        self.card_paye.grid(row=0, column=2, padx=5, sticky="nsew")
        self.card_impayees = StatCard(cards, "Factures impayées", "0", "📋", "warning")
        self.card_impayees.grid(row=0, column=3, padx=5, sticky="nsew")
        self.card_retard = StatCard(cards, "En retard", "0", "🔴", "danger")
        self.card_retard.grid(row=0, column=4, padx=5, sticky="nsew")
        self.card_echeance = StatCard(cards, "Échéances 7 jours", "0", "📅", "secondary")
        self.card_echeance.grid(row=0, column=5, padx=5, sticky="nsew")

        self.search = SearchBar(self, command=self.search_supplier)
        self.search.pack(fill=X, padx=20, pady=(0, 15))

        content = tb.Frame(self)
        content.pack(fill=BOTH, expand=True, padx=20, pady=10)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self.left_panel = tb.Frame(content)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.right_panel = tb.Frame(content)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        self.build_supplier_debts()
        self.build_notifications()
        self.build_due()

    def build_supplier_debts(self):
        header = tb.Frame(self.left_panel)
        header.pack(fill=X, pady=(0, 10))
        tb.Label(
            header,
            text="Dettes fournisseurs",
            font=("Segoe UI", 16, "bold"),
        ).pack(side=LEFT)
        self.debt_summary = tb.Label(
            header,
            text="Factures non réglées, regroupées par fournisseur",
            bootstyle="secondary",
        )
        self.debt_summary.pack(side=LEFT, padx=15)

        container = tb.Frame(self.left_panel)
        container.pack(fill=BOTH, expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.debt_canvas = tk.Canvas(container, highlightthickness=0, borderwidth=0)
        self.debt_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.debt_canvas.yview)
        self.debt_canvas.configure(yscrollcommand=self.debt_scrollbar.set)
        self.debt_canvas.grid(row=0, column=0, sticky="nsew")
        self.debt_scrollbar.grid(row=0, column=1, sticky="ns")

        self.debt_inner = tb.Frame(self.debt_canvas)
        self.debt_window = self.debt_canvas.create_window((0, 0), window=self.debt_inner, anchor="nw")
        self.debt_inner.bind("<Configure>", self._on_debt_configure)
        self.debt_canvas.bind("<Configure>", self._on_debt_canvas_configure)
        self.debt_canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_debt_configure(self, _event=None):
        self.debt_canvas.configure(scrollregion=self.debt_canvas.bbox("all"))

    def _on_debt_canvas_configure(self, event):
        self.debt_canvas.itemconfigure(self.debt_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.debt_canvas.winfo_exists():
            self.debt_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def build_notifications(self):
        frame = tb.Labelframe(self.right_panel, text="🔔 Alertes", padding=12)
        frame.pack(fill=X, pady=(0, 15))
        self.notification_frame = tb.Frame(frame)
        self.notification_frame.pack(fill=X)

    def build_due(self):
        frame = tb.Labelframe(self.right_panel, text="⏰ Prochaines échéances", padding=12)
        frame.pack(fill=BOTH, expand=True)
        self.due_frame = tb.Frame(frame)
        self.due_frame.pack(fill=BOTH, expand=True)

    def refresh_dashboard(self):
        try:
            self.data = DashboardService.get_dashboard_data()
            self.refresh_cards()
            self.refresh_supplier_debts()
            self.refresh_notifications()
            self.refresh_due()
        except Exception as e:
            print("Erreur Dashboard :", e)

    def refresh_cards(self):
        self.card_factures.set_value(str(self.data.get("total_factures", 0)))
        self.card_dette.set_value(self.format_amount(self.data.get("reste", 0)))
        self.card_paye.set_value(self.format_amount(self.data.get("montant_paye", 0)))
        self.card_impayees.set_value(str(self.data.get("nombre_factures_impayees", 0)))
        self.card_retard.set_value(str(self.data.get("retard", 0)))
        self.card_echeance.set_value(str(self.data.get("echeance", 0)))

    def refresh_supplier_debts(self, search_text=""):
        for widget in self.debt_inner.winfo_children():
            widget.destroy()

        fournisseurs = self.data.get("dettes_fournisseurs", [])
        texte = str(search_text or "").strip().lower()
        if texte:
            fournisseurs = [
                fournisseur for fournisseur in fournisseurs
                if texte in fournisseur["fournisseur_nom"].lower()
                or any(
                    texte in str(facture["numero"]).lower()
                    for facture in fournisseur["factures"]
                )
            ]

        if not fournisseurs:
            tb.Label(
                self.debt_inner,
                text="✓ Aucune facture impayée pour les fournisseurs sélectionnés",
                bootstyle="success",
                font=("Segoe UI", 11),
            ).pack(anchor="w", padx=10, pady=15)
            return

        total_dette = sum(item["dette"] for item in fournisseurs)
        self.debt_summary.configure(
            text=f"{len(fournisseurs)} fournisseur(s) • {self.format_amount(total_dette)} de dette"
        )

        for fournisseur in fournisseurs:
            self._build_supplier_section(fournisseur)

    def _build_supplier_section(self, fournisseur):
        section = tb.Labelframe(
            self.debt_inner,
            text=f"  {fournisseur['fournisseur_nom']}  ",
            padding=10,
        )
        section.pack(fill=X, padx=5, pady=(0, 12))

        summary = tb.Frame(section)
        summary.pack(fill=X, pady=(0, 8))

        tb.Label(
            summary,
            text=f"{fournisseur['nombre_factures']} facture(s) non réglée(s)",
            font=("Segoe UI", 10, "bold"),
        ).pack(side=LEFT)
        tb.Label(
            summary,
            text=f"Dette : {self.format_amount(fournisseur['dette'])}",
            bootstyle="danger",
            font=("Segoe UI", 11, "bold"),
        ).pack(side=RIGHT)

        columns = ("Numéro", "Date", "Échéance", "Montant", "Payé", "Reste", "Statut")
        tree = ttk.Treeview(section, columns=columns, show="headings", height=min(6, max(2, len(fournisseur["factures"]))))
        widths = {
            "Numéro": 110,
            "Date": 90,
            "Échéance": 95,
            "Montant": 105,
            "Payé": 105,
            "Reste": 105,
            "Statut": 150,
        }
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=widths[column], anchor="center")

        for facture in fournisseur["factures"]:
            date_echeance = facture["date_echeance"]
            statut = facture["statut"]
            if date_echeance and date_echeance < date.today():
                statut = "EN RETARD"
            tree.insert("", "end", values=(
                facture["numero"],
                facture["date_facture"],
                date_echeance,
                self.format_amount(facture["montant"]),
                self.format_amount(facture["montant_paye"]),
                self.format_amount(facture["reste"]),
                statut,
            ))

        tree.pack(fill=X, expand=True)

    def refresh_notifications(self):
        for widget in self.notification_frame.winfo_children():
            widget.destroy()

        notifications = self.data.get("notifications", [])
        if not notifications:
            tb.Label(
                self.notification_frame,
                text="✓ Aucune alerte",
                bootstyle="success",
            ).pack(anchor="w", pady=5)
            return

        for notification in notifications:
            text = notification.lower()
            style = "danger" if "retard" in text or "dette" in text else "warning"
            tb.Label(
                self.notification_frame,
                text=f"• {notification}",
                bootstyle=style,
                wraplength=300,
                justify="left",
            ).pack(anchor="w", pady=5)

    def refresh_due(self):
        for widget in self.due_frame.winfo_children():
            widget.destroy()

        factures = self.data.get("echeances", [])
        if not factures:
            tb.Label(
                self.due_frame,
                text="✓ Aucune échéance à surveiller",
                bootstyle="success",
            ).pack(anchor="w", pady=5)
            return

        aujourd_hui = date.today()
        for facture in factures:
            date_echeance = getattr(facture, "date_echeance", None)
            est_retard = date_echeance is not None and date_echeance < aujourd_hui
            statut = "EN RETARD" if est_retard else "À VENIR"
            style = "danger" if est_retard else "warning"
            fournisseur = getattr(facture, "fournisseur", None)
            fournisseur_nom = getattr(fournisseur, "nom", "Fournisseur") if fournisseur else "Fournisseur"
            numero = getattr(facture, "numero", facture.id)
            reste = float(getattr(facture, "reste", 0) or 0)
            texte = (
                f"{fournisseur_nom} • {numero}\n"
                f"Échéance : {date_echeance}\n"
                f"Reste : {self.format_amount(reste)}"
            )
            item = tb.Frame(self.due_frame, padding=8)
            item.pack(fill=X, pady=4)
            tb.Label(item, text=statut, bootstyle=style, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tb.Label(item, text=texte, justify="left", font=("Segoe UI", 9)).pack(anchor="w")

    def search_supplier(self, texte):
        self.refresh_supplier_debts(texte)

    @staticmethod
    def format_amount(amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0
        return f"{amount:,.2f} DA"
