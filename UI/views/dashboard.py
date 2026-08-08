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
    """Dashboard moderne et aéré, centré sur les dettes fournisseurs."""

    def __init__(self, master):
        super().__init__(master, "Tableau de bord")
        self.data = {}
        self.build()
        self.refresh_dashboard()

    def build(self):
        root = self.body
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        header = tb.Frame(root)
        header.grid(row=0, column=0, sticky="ew", padx=4, pady=(2, 8))
        header.columnconfigure(0, weight=1)
        tb.Label(header, text="Situation financière", font=("Segoe UI", 17, "bold")).grid(row=0, column=0, sticky="w")
        tb.Label(header, text="Priorité : fournisseurs à régler", bootstyle="secondary").grid(row=1, column=0, sticky="w")
        tb.Button(header, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh_dashboard, padding=(10, 6)).grid(row=0, column=1, rowspan=2, sticky="e")

        cards = tb.Frame(root)
        cards.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 10))
        for i in range(4):
            cards.columnconfigure(i, weight=1)
        self.card_dette = StatCard(cards, "Dette nette", "0 DA", "💳", "danger")
        self.card_dette.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.card_impayees = StatCard(cards, "Factures à régler", "0", "📋", "warning")
        self.card_impayees.grid(row=0, column=1, padx=5, sticky="ew")
        self.card_avoirs = StatCard(cards, "Avoirs disponibles", "0 DA", "↩", "info")
        self.card_avoirs.grid(row=0, column=2, padx=5, sticky="ew")
        self.card_retard = StatCard(cards, "En retard", "0", "!", "danger")
        self.card_retard.grid(row=0, column=3, padx=(5, 0), sticky="ew")

        content = tb.Frame(root)
        content.grid(row=2, column=0, sticky="nsew", padx=4)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=1, minsize=260)
        content.rowconfigure(1, weight=1)

        self.search = SearchBar(content, command=self.search_supplier)
        self.search.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        left = tb.Frame(content)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 9))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        title = tb.Frame(left)
        title.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tb.Label(title, text="Fournisseurs à régler", font=("Segoe UI", 14, "bold")).pack(side=LEFT)
        self.debt_summary = tb.Label(title, text="", bootstyle="secondary")
        self.debt_summary.pack(side=LEFT, padx=10)

        scroll = tb.Frame(left)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.rowconfigure(0, weight=1)
        scroll.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(scroll, highlightthickness=0, borderwidth=0)
        bar = ttk.Scrollbar(scroll, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        bar.grid(row=0, column=1, sticky="ns")
        self.inner = tb.Frame(self.canvas)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        # Le binding est local au Canvas. bind_all() gardait des callbacks vers
        # des Canvas détruits après un changement de vue et provoquait
        # "invalid command name ...canvas".
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        right = tb.Frame(content)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        alerts = tb.Labelframe(right, text="  🔔 Alertes  ", padding=10)
        alerts.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.alerts = tb.Frame(alerts)
        self.alerts.pack(fill=X)
        due = tb.Labelframe(right, text="  ⏰ Échéances  ", padding=10)
        due.grid(row=1, column=0, sticky="nsew")
        self.due = tb.Frame(due)
        self.due.pack(fill=BOTH, expand=True)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def refresh_dashboard(self):
        try:
            self.data = DashboardService.get_dashboard_data()
            self.refresh_cards()
            self.refresh_suppliers()
            self.refresh_alerts()
            self.refresh_due()
            # Synchronise immédiatement le badge du centre de notifications
            # après chaque actualisation du Dashboard.
            root = self.winfo_toplevel()
            topbar = getattr(root, "topbar", None)
            if topbar is not None and topbar.winfo_exists() and hasattr(topbar, "set_notification_count"):
                count = int(self.data.get("retard", 0) or 0) + int(self.data.get("echeance", 0) or 0)
                topbar.set_notification_count(count)
        except Exception as exc:
            print("Erreur Dashboard :", exc)

    def refresh_cards(self):
        self.card_dette.set_value(self.format_amount(self.data.get("reste", 0)))
        self.card_impayees.set_value(str(self.data.get("nombre_factures_impayees", 0)))
        credit = sum(float(x.get("credit_disponible", 0) or 0) for x in self.data.get("dettes_fournisseurs", []))
        self.card_avoirs.set_value(self.format_amount(credit))
        self.card_retard.set_value(str(self.data.get("retard", 0)))

    def refresh_suppliers(self, search_text=""):
        for w in self.inner.winfo_children():
            w.destroy()
        suppliers = self.data.get("dettes_fournisseurs", [])
        q = str(search_text or "").strip().lower()
        if q:
            suppliers = [s for s in suppliers if q in s.get("fournisseur_nom", "").lower() or any(q in str(f.get("numero", "")).lower() for f in s.get("factures", []))]
        if not suppliers:
            self.debt_summary.configure(text="Aucune dette")
            tb.Label(self.inner, text="✓ Aucun règlement en attente", bootstyle="success", font=("Segoe UI", 11)).pack(anchor="w", padx=8, pady=15)
            return
        total = sum(float(s.get("dette", 0) or 0) for s in suppliers)
        self.debt_summary.configure(text=f"{len(suppliers)} fournisseur(s) • {self.format_amount(total)}")
        for s in suppliers:
            self.add_supplier(s)

    def add_supplier(self, supplier):
        box = tb.Labelframe(self.inner, text=f"  {supplier.get('fournisseur_nom', 'Fournisseur')}  ", padding=9)
        box.pack(fill=X, padx=1, pady=(0, 8))
        top = tb.Frame(box)
        top.pack(fill=X, pady=(0, 6))
        tb.Label(top, text=f"{supplier.get('nombre_factures_impayees', 0)} facture(s) impayée(s)", font=("Segoe UI", 9, "bold")).pack(side=LEFT)
        debt = float(supplier.get("dette", 0) or 0)
        credit = float(supplier.get("credit_disponible", 0) or 0)
        tb.Label(top, text=f"Dette : {self.format_amount(debt)}" if debt >= 0 else f"Crédit : {self.format_amount(abs(debt))}", bootstyle="danger" if debt >= 0 else "success", font=("Segoe UI", 10, "bold")).pack(side=RIGHT)
        if credit > 0:
            tb.Label(top, text=f"Avoir : {self.format_amount(credit)}", bootstyle="info").pack(side=RIGHT, padx=10)

        cols = ("Numéro", "Échéance", "Reste", "Statut")
        tree = ttk.Treeview(box, columns=cols, show="headings", height=min(4, max(2, len(supplier.get("factures", [])))))
        for c, width in zip(cols, (150, 120, 140, 130)):
            tree.heading(c, text=c)
            tree.column(c, width=width, anchor="center")
        for f in supplier.get("factures", []):
            echeance = f.get("date_echeance")
            statut = f.get("statut", "Impayée")
            if echeance and echeance < date.today() and f.get("type_piece") != "Avoir":
                statut = "EN RETARD"
            tree.insert("", "end", values=(f.get("numero", ""), self.format_date(echeance), self.format_amount(f.get("reste", 0)), statut))
        tree.pack(fill=X)
        action = tb.Frame(box)
        action.pack(fill=X, pady=(7, 0))
        tb.Button(action, text="💰 Régler les factures", bootstyle="success", command=lambda s=supplier: self.open_supplier_payment(s)).pack(side=RIGHT)
        tb.Button(action, text="Voir les factures", bootstyle="secondary-outline", command=lambda s=supplier: self.open_supplier_factures(s)).pack(side=RIGHT, padx=(0, 7))
        tree.bind("<Double-1>", lambda _e, s=supplier: self.open_supplier_payment(s))

    def open_supplier_payment(self, supplier):
        root = self.winfo_toplevel()
        if not hasattr(root, "show_paiements"):
            return
        root.show_paiements()
        view = getattr(root, "current_view", None)
        if view is not None and hasattr(view, "open_bulk_payment_dialog"):
            view.open_bulk_payment_dialog(fournisseur_id=supplier.get("fournisseur_id"), fournisseur_nom=supplier.get("fournisseur_nom"))

    def open_supplier_factures(self, supplier):
        root = self.winfo_toplevel()
        if hasattr(root, "show_factures"):
            root.show_factures()

    def refresh_alerts(self):
        for w in self.alerts.winfo_children():
            w.destroy()
        retard = int(self.data.get("retard", 0) or 0)
        echeance = int(self.data.get("echeance", 0) or 0)
        if retard:
            tb.Label(self.alerts, text=f"🔴 {retard} facture(s) en retard", bootstyle="danger").pack(anchor="w", pady=3)
        if echeance:
            tb.Label(self.alerts, text=f"🟠 {echeance} échéance(s) sous 7 jours", bootstyle="warning", wraplength=280).pack(anchor="w", pady=3)
        if not retard and not echeance:
            tb.Label(self.alerts, text="✓ Aucune alerte", bootstyle="success").pack(anchor="w")

    def refresh_due(self):
        for w in self.due.winfo_children():
            w.destroy()
        items = []
        for s in self.data.get("dettes_fournisseurs", []):
            for f in s.get("factures", []):
                if f.get("type_piece") != "Avoir" and float(f.get("reste", 0) or 0) > 0 and f.get("date_echeance"):
                    items.append((f.get("date_echeance"), s.get("fournisseur_nom", ""), f.get("numero", ""), f.get("reste", 0)))
        items.sort(key=lambda x: x[0])
        if not items:
            tb.Label(self.due, text="Aucune échéance en attente", bootstyle="success").pack(anchor="w", pady=8)
            return
        for due_date, supplier, number, remaining in items[:8]:
            row = tb.Frame(self.due, padding=(2, 6))
            row.pack(fill=X)
            tb.Label(row, text=self.format_date(due_date), width=11).pack(side=LEFT)
            tb.Label(row, text=supplier, font=("Segoe UI", 9, "bold"), anchor="w").pack(side=LEFT, fill=X, expand=True)
            tb.Label(row, text=self.format_amount(remaining), bootstyle="danger").pack(side=RIGHT)

    def search_supplier(self, text=""):
        self.refresh_suppliers(text)

    @staticmethod
    def format_date(value):
        if not value:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        try:
            return date.fromisoformat(str(value)[:10]).strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def format_amount(value):
        try:
            return f"{float(value or 0):,.2f} DA".replace(",", " ")
        except (TypeError, ValueError):
            return "0.00 DA"
