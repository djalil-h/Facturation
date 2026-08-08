import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.base_view import BaseView
from UI.widgets.stat_card import StatCard
from UI.widgets.search_bar import SearchBar
from services.dashboard_service import DashboardService
from services.facture_service import regler_plusieurs_factures


class Dashboard(BaseView):
    """Dashboard orienté dettes fournisseurs et règlements."""

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
        tb.Label(header, text="Dettes fournisseurs", font=("Segoe UI", 16, "bold")).pack(side=LEFT)
        self.debt_summary = tb.Label(header, text="Factures non réglées, regroupées par fournisseur", bootstyle="secondary")
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
        except Exception as exc:
            print("Erreur Dashboard :", exc)

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
            fournisseurs = [f for f in fournisseurs if texte in f["fournisseur_nom"].lower() or any(texte in str(x["numero"]).lower() for x in f["factures"])]
        if not fournisseurs:
            self.debt_summary.configure(text="Aucune dette fournisseur")
            tb.Label(self.debt_inner, text="✓ Aucune facture impayée pour les fournisseurs sélectionnés", bootstyle="success", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=15)
            return
        total_dette = sum(item["dette"] for item in fournisseurs)
        self.debt_summary.configure(text=f"{len(fournisseurs)} fournisseur(s) • {self.format_amount(total_dette)} de dette")
        for fournisseur in fournisseurs:
            self._build_supplier_section(fournisseur)

    def _build_supplier_section(self, fournisseur):
        section = tb.Labelframe(self.debt_inner, text=f"  {fournisseur['fournisseur_nom']}  ", padding=10)
        section.pack(fill=X, padx=5, pady=(0, 12))
        summary = tb.Frame(section)
        summary.pack(fill=X, pady=(0, 8))
        tb.Label(summary, text=f"{fournisseur['nombre_factures_impayees']} facture(s) non réglée(s)", font=("Segoe UI", 10, "bold")).pack(side=LEFT)
        dette = float(fournisseur.get("dette", 0) or 0)
        credit = float(fournisseur.get("credit_disponible", 0) or 0)
        if dette >= 0:
            label = f"Dette : {self.format_amount(dette)}"
            style = "danger"
        else:
            label = f"Crédit fournisseur : {self.format_amount(abs(dette))}"
            style = "success"
        tb.Label(summary, text=label, bootstyle=style, font=("Segoe UI", 11, "bold")).pack(side=RIGHT)
        if credit > 0:
            tb.Label(summary, text=f"Avoir disponible : {self.format_amount(credit)}", bootstyle="info").pack(side=RIGHT, padx=15)
        actions = tb.Frame(section)
        actions.pack(fill=X, pady=(0, 8))
        tb.Button(actions, text="Voir le détail / régler", bootstyle="primary-outline", command=lambda item=fournisseur: self.open_supplier_detail(item)).pack(side=RIGHT)
        columns = ("Numéro", "Date", "Échéance", "Montant", "Payé", "Reste", "Statut")
        tree = ttk.Treeview(section, columns=columns, show="headings", height=min(6, max(2, len(fournisseur["factures"]))))
        widths = {"Numéro": 110, "Date": 90, "Échéance": 95, "Montant": 105, "Payé": 105, "Reste": 105, "Statut": 150}
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=widths[column], anchor="center")
        for facture in fournisseur["factures"]:
            echeance = facture["date_echeance"]
            statut = facture["statut"]
            if echeance and echeance < date.today() and facture.get("type_piece") != "Avoir":
                statut = "EN RETARD"
            tree.insert("", "end", values=(facture["numero"], facture["date_facture"], echeance, self.format_amount(facture["montant"]), self.format_amount(facture["montant_paye"]), self.format_amount(facture["reste"]), statut))
        tree.pack(fill=X, expand=True)
        tree.bind("<Double-1>", lambda _event, item=fournisseur: self.open_supplier_detail(item))

    def open_supplier_detail(self, fournisseur):
        factures = [f for f in fournisseur.get("factures", []) if f.get("type_piece") != "Avoir" and float(f.get("reste", 0) or 0) > 0]
        dialog = tb.Toplevel(self)
        dialog.title(f"Dette fournisseur - {fournisseur['fournisseur_nom']}")
        dialog.geometry("900x680")
        dialog.minsize(800, 580)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=20)
        box.pack(fill=BOTH, expand=True)
        box.columnconfigure(0, weight=1)
        box.rowconfigure(2, weight=1)

        header = tb.Frame(box)
        header.grid(row=0, column=0, sticky="ew")
        tb.Label(header, text=fournisseur["fournisseur_nom"], font=("Segoe UI", 22, "bold")).pack(side=LEFT)
        dette = float(fournisseur.get("dette", 0) or 0)
        credit = float(fournisseur.get("credit_disponible", 0) or 0)
        if dette >= 0:
            tb.Label(header, text=f"Dette nette : {self.format_amount(dette)}", bootstyle="danger", font=("Segoe UI", 14, "bold")).pack(side=RIGHT)
        else:
            tb.Label(header, text=f"Crédit : {self.format_amount(abs(dette))}", bootstyle="success", font=("Segoe UI", 14, "bold")).pack(side=RIGHT)
        subtitle = f"{len(factures)} facture(s) avec un reste à payer"
        if credit > 0:
            subtitle += f" • Avoir disponible : {self.format_amount(credit)}"
        tb.Label(box, text=subtitle, bootstyle="secondary").grid(row=1, column=0, sticky="w", pady=(5, 8))

        controls = tb.Frame(box)
        controls.grid(row=2, column=0, sticky="nsew")
        controls.rowconfigure(1, weight=1)
        controls.columnconfigure(0, weight=1)

        selection_bar = tb.Frame(controls)
        selection_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        selected_label = tb.Label(selection_bar, text="0 facture sélectionnée")
        selected_label.pack(side=LEFT)

        frame = tb.Frame(controls)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tb.Frame(canvas)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        selections = {}
        for facture in factures:
            var = tk.BooleanVar(value=False)
            selections[facture["id"]] = var
            row = tb.Frame(inner, padding=8, bootstyle="light")
            row.pack(fill=X, pady=3)
            text = f"{facture['numero']}   |   Échéance : {facture['date_echeance']}   |   Montant : {self.format_amount(facture['montant'])}   |   Payé : {self.format_amount(facture['montant_paye'])}   |   Reste : {self.format_amount(facture['reste'])}"
            cb = tb.Checkbutton(row, text=text, variable=var, bootstyle="primary")
            cb.pack(side=LEFT, fill=X, expand=True, anchor="w")

        if not factures:
            tb.Label(inner, text="✓ Aucune dette sur ce fournisseur.", bootstyle="success").pack(anchor="w", pady=20)

        total_var = tk.StringVar(value="Total à payer : 0.00 DA")
        credit_var = tk.StringVar(value="Avoir imputable : 0.00 DA")
        tb.Label(box, textvariable=credit_var, bootstyle="info", font=("Segoe UI", 11)).grid(row=3, column=0, sticky="w", pady=(12, 2))
        tb.Label(box, textvariable=total_var, font=("Segoe UI", 13, "bold")).grid(row=4, column=0, sticky="w", pady=(0, 8))

        def update_total(*_):
            ids = [fid for fid, var in selections.items() if var.get()]
            brut = sum(float(f["reste"] or 0) for f in factures if selections[f["id"]].get())
            avoir_imputable = min(brut, credit)
            cash = max(0.0, brut - avoir_imputable)
            selected_label.configure(text=f"{len(ids)} facture(s) sélectionnée(s)")
            credit_var.set(f"Avoir imputable sur cette sélection : {avoir_imputable:,.2f} DA")
            total_var.set(f"Total à payer après avoir : {cash:,.2f} DA")

        def select_all():
            for var in selections.values():
                var.set(True)
            update_total()

        def clear_all():
            for var in selections.values():
                var.set(False)
            update_total()

        tb.Button(selection_bar, text="☑ Tout sélectionner", bootstyle="secondary-outline", command=select_all).pack(side=LEFT, padx=5)
        tb.Button(selection_bar, text="☐ Tout désélectionner", bootstyle="secondary-outline", command=clear_all).pack(side=LEFT, padx=5)
        for var in selections.values():
            var.trace_add("write", update_total)

        form = tb.Frame(box)
        form.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        tb.Label(form, text="Mode").pack(side=LEFT, padx=(0, 8))
        mode = tb.Combobox(form, state="readonly", values=["Espèces", "Chèque", "Virement", "Carte", "Autre"], width=16)
        mode.current(0)
        mode.pack(side=LEFT, padx=(0, 20))
        tb.Label(form, text="Référence").pack(side=LEFT, padx=(0, 8))
        reference = tb.Entry(form, width=30)
        reference.pack(side=LEFT, fill=X, expand=True)

        buttons = tb.Frame(box)
        buttons.grid(row=6, column=0, sticky="ew", pady=(8, 0))

        def pay_selected():
            ids = [fid for fid, var in selections.items() if var.get()]
            if not ids:
                messagebox.showwarning("Règlement", "Sélectionnez au moins une facture.", parent=dialog)
                return
            brut = sum(float(f["reste"] or 0) for f in factures if selections[f["id"]].get())
            avoir_imputable = min(brut, credit)
            cash = max(0.0, brut - avoir_imputable)
            confirmation = (
                f"Factures sélectionnées : {len(ids)}\n"
                f"Total avant avoir : {brut:,.2f} DA\n"
                f"Avoir imputé : {avoir_imputable:,.2f} DA\n"
                f"Montant réellement payé : {cash:,.2f} DA\n\n"
                "Confirmer le règlement ?"
            )
            if not messagebox.askyesno("Confirmer le règlement", confirmation, parent=dialog):
                return
            try:
                result = regler_plusieurs_factures(ids, mode.get(), reference.get().strip(), self.winfo_toplevel().get_current_user())
            except Exception as exc:
                messagebox.showerror("Règlement refusé", str(exc), parent=dialog)
                return
            messagebox.showinfo(
                "Règlement effectué",
                f"{result['factures']} facture(s) traitée(s).\n"
                f"Avoir imputé : {result['avoir_impute']:,.2f} DA\n"
                f"Total payé : {result['total']:,.2f} DA",
                parent=dialog,
            )
            dialog.destroy()
            self.refresh_dashboard()

        tb.Button(buttons, text="Fermer", bootstyle="secondary-outline", command=dialog.destroy).pack(side=RIGHT, padx=5)
        tb.Button(buttons, text="💰 Régler les factures sélectionnées", bootstyle="success", command=pay_selected).pack(side=RIGHT)
        update_total()

    def refresh_notifications(self):
        for widget in self.notification_frame.winfo_children():
            widget.destroy()
        retard = int(self.data.get("retard", 0) or 0)
        echeance = int(self.data.get("echeance", 0) or 0)
        if retard:
            tb.Label(self.notification_frame, text=f"🔴 {retard} facture(s) en retard", bootstyle="danger", wraplength=300).pack(anchor="w", pady=3)
        if echeance:
            tb.Label(self.notification_frame, text=f"🟠 {echeance} facture(s) arrivent à échéance sous 7 jours", bootstyle="warning", wraplength=300).pack(anchor="w", pady=3)
        if not retard and not echeance:
            tb.Label(self.notification_frame, text="✓ Aucune alerte", bootstyle="success").pack(anchor="w")

    def refresh_due(self):
        for widget in self.due_frame.winfo_children():
            widget.destroy()
        dues = self.data.get("prochaines_echeances", self.data.get("dernieres", [])) or []
        dues = [f for f in dues if float(getattr(f, "reste", 0) or 0) > 0]
        if not dues:
            tb.Label(self.due_frame, text="Aucune échéance à venir", bootstyle="success").pack(anchor="w", pady=10)
            return
        for facture in dues[:10]:
            fournisseur = getattr(getattr(facture, "fournisseur", None), "nom", "") or "Fournisseur non renseigné"
            tb.Label(self.due_frame, text=f"{facture.numero} — {fournisseur}\nÉchéance : {facture.date_echeance}\nReste : {self.format_amount(facture.reste)}", wraplength=300).pack(anchor="w", pady=7)

    def search_supplier(self, text=""):
        if hasattr(self.search, "get_value"):
            try:
                text = self.search.get_value()
            except Exception:
                pass
        self.refresh_supplier_debts(text)

    @staticmethod
    def format_amount(value):
        try:
            return f"{float(value or 0):,.2f} DA"
        except (TypeError, ValueError):
            return "0.00 DA"
