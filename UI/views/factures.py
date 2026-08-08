import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.facture_service import (
    ajouter_facture,
    liste_factures,
    modifier_facture,
    supprimer_facture,
    ajouter_paiement,
    liste_paiements,
    rechercher_factures,
)
from services.fournisseur_service import liste_fournisseurs


class FacturesView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Gestion des factures")
        self.factures = []
        self.fournisseurs = []
        self._build()
        self.refresh()

    def _current_user(self):
        return self.winfo_toplevel().get_current_user()

    def _build(self):
        header = tb.Frame(self.body)
        header.pack(fill="x", pady=(0, 15))
        tb.Label(header, text="Factures", font=("Segoe UI", 22, "bold")).pack(side="left")
        tb.Button(header, text="＋ Nouvelle facture", bootstyle="success", command=self.open_add_dialog).pack(side="right")

        toolbar = tb.Frame(self.body)
        toolbar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        tb.Entry(toolbar, textvariable=self.search_var, width=35).pack(side="left", ipady=5)
        tb.Label(toolbar, text="  Numéro / fournisseur").pack(side="left")
        self.status_var = tk.StringVar(value="Tous les statuts")
        self.status_combo = tb.Combobox(
            toolbar, textvariable=self.status_var, state="readonly", width=22,
            values=["Tous les statuts", "Impayée", "Partiellement payée", "Payée"]
        )
        self.status_combo.pack(side="left", padx=15)
        self.status_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(toolbar, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh).pack(side="right")

        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "N° Facture", "Fournisseur", "Date", "Échéance", "Montant", "Payé", "Reste", "Statut"))
        self.table.pack(fill="both", expand=True)
        self.table.bind_double_click(self._edit_selected)

        footer = tb.Frame(self.body)
        footer.pack(fill="x", pady=(12, 0))
        self.count_label = tb.Label(footer, text="0 facture")
        self.count_label.pack(side="left")
        for text, style, command in [
            ("✎ Modifier", "primary-outline", self._edit_selected),
            ("💰 Paiement", "success-outline", self.open_payment_dialog),
            ("✕ Supprimer", "danger-outline", self._delete_selected),
        ]:
            tb.Button(footer, text=text, bootstyle=style, command=command).pack(side="right", padx=4)

    def refresh(self):
        try:
            self.fournisseurs = liste_fournisseurs()
            status = self.status_var.get() if hasattr(self, "status_var") else "Tous les statuts"
            enum_status = None if status == "Tous les statuts" else status
            search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
            self.factures = rechercher_factures(statut=enum_status)
            if search:
                self.factures = [
                    f for f in self.factures
                    if search in str(f.numero).lower()
                    or search in str(getattr(f.fournisseur, "nom", "")).lower()
                ]
        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les factures.\n\n{exc}")
            return

        rows = []
        for f in self.factures:
            rows.append((
                f.id, f.numero,
                getattr(f.fournisseur, "nom", "") if f.fournisseur else "",
                f.date_facture, f.date_echeance,
                f"{f.montant:,.2f} DA", f"{f.montant_paye:,.2f} DA",
                f"{f.reste:,.2f} DA", getattr(f.statut, "value", f.statut),
            ))
        self.table.load_data(rows)
        self.table.autosize()
        self.count_label.configure(text=f"{len(rows)} facture{'s' if len(rows) != 1 else ''}")

    def _selected(self):
        values = self.table.get_selected()
        if not values:
            messagebox.showwarning("Sélection", "Sélectionnez une facture.")
            return None
        try:
            selected_id = int(values[0])
        except (TypeError, ValueError):
            return None
        return next((f for f in self.factures if f.id == selected_id), None)

    def _edit_selected(self, _event=None):
        facture = self._selected()
        if facture:
            self.open_form_dialog(facture)

    def _delete_selected(self):
        facture = self._selected()
        if not facture:
            return
        if not messagebox.askyesno("Confirmation", f"Supprimer la facture « {facture.numero} » ?"):
            return
        try:
            supprimer_facture(facture.id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", f"Suppression impossible.\n\n{exc}")

    def _fournisseur_map(self):
        return {f.nom: f.id for f in self.fournisseurs}

    def open_add_dialog(self):
        self.open_form_dialog(None)

    def open_form_dialog(self, facture):
        dialog = tb.Toplevel(self)
        dialog.title("Modifier la facture" if facture else "Nouvelle facture")
        dialog.geometry("600x650")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Modifier la facture" if facture else "Nouvelle facture", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 18))

        entries = {}
        for label, key, value in [
            ("Numéro *", "numero", getattr(facture, "numero", "")),
            ("Date facture (AAAA-MM-JJ) *", "date_facture", getattr(facture, "date_facture", date.today())),
            ("Date échéance (AAAA-MM-JJ) *", "date_echeance", getattr(facture, "date_echeance", date.today())),
            ("Montant *", "montant", getattr(facture, "montant", "")),
            ("Commentaire", "commentaire", getattr(facture, "commentaire", "") or ""),
        ]:
            tb.Label(box, text=label).pack(anchor="w", pady=(7, 3))
            e = tb.Entry(box)
            e.insert(0, str(value))
            e.pack(fill="x")
            entries[key] = e

        tb.Label(box, text="Fournisseur *").pack(anchor="w", pady=(7, 3))
        names = list(self._fournisseur_map().keys())
        fournisseur_var = tk.StringVar()
        combo = tb.Combobox(box, textvariable=fournisseur_var, state="readonly", values=names)
        combo.pack(fill="x")
        if facture and facture.fournisseur:
            fournisseur_var.set(facture.fournisseur.nom)
        elif names:
            combo.current(0)

        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=(25, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)

        def save():
            numero = entries["numero"].get().strip()
            if not numero or not fournisseur_var.get():
                messagebox.showwarning("Validation", "Numéro et fournisseur sont obligatoires.", parent=dialog)
                return
            try:
                d_facture = datetime.strptime(entries["date_facture"].get().strip(), "%Y-%m-%d").date()
                d_echeance = datetime.strptime(entries["date_echeance"].get().strip(), "%Y-%m-%d").date()
                montant = float(entries["montant"].get().replace(",", "."))
                if montant < 0:
                    raise ValueError("Le montant doit être positif.")
                fournisseur_id = self._fournisseur_map()[fournisseur_var.get()]
                utilisateur = self._current_user()
                if facture:
                    modifier_facture(facture.id, fournisseur_id, numero, d_facture, d_echeance, montant, entries["commentaire"].get().strip(), utilisateur)
                else:
                    ajouter_facture(numero, fournisseur_id, d_facture, d_echeance, montant, entries["commentaire"].get().strip(), utilisateur)
            except Exception as exc:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer la facture.\n\n{exc}", parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        tb.Button(buttons, text="Enregistrer", bootstyle="success", command=save).pack(side="right")

    def open_payment_dialog(self):
        facture = self._selected()
        if not facture:
            return
        if facture.reste <= 0:
            messagebox.showinfo("Paiement", "Cette facture est déjà entièrement payée.")
            return

        dialog = tb.Toplevel(self)
        dialog.title(f"Paiement — {facture.numero}")
        dialog.geometry("500x430")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Enregistrer un paiement", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(box, text=f"Facture : {facture.numero}\nReste à payer : {facture.reste:,.2f} DA", font=("Segoe UI", 11)).pack(anchor="w", pady=15)

        tb.Label(box, text="Montant *").pack(anchor="w", pady=(5, 3))
        amount = tb.Entry(box)
        amount.insert(0, str(facture.reste))
        amount.pack(fill="x")
        tb.Label(box, text="Mode de paiement").pack(anchor="w", pady=(10, 3))
        mode = tb.Combobox(box, state="readonly", values=["Espèces", "Chèque", "Virement", "Carte", "Autre"])
        mode.current(0)
        mode.pack(fill="x")
        tb.Label(box, text="Référence").pack(anchor="w", pady=(10, 3))
        reference = tb.Entry(box)
        reference.pack(fill="x")

        def save():
            try:
                montant = float(amount.get().replace(",", "."))
                ajouter_paiement(facture.id, montant, mode.get(), reference.get().strip(), self._current_user())
            except Exception as exc:
                messagebox.showerror("Paiement refusé", str(exc), parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=25)
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)
        tb.Button(buttons, text="Enregistrer le paiement", bootstyle="success", command=save).pack(side="right")

    def show_payments(self):
        facture = self._selected()
        if not facture:
            return
        paiements = liste_paiements(facture.id)
        if not paiements:
            messagebox.showinfo("Paiements", "Aucun paiement enregistré.")
            return
        details = "\n".join(f"{p.date_paiement} — {p.montant:,.2f} DA — {p.mode_paiement or '-'} — {p.reference or '-'}" for p in paiements)
        messagebox.showinfo(f"Paiements — {facture.numero}", details)
