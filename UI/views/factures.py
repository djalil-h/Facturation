import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import date, datetime
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.facture_service import ajouter_facture, liste_factures, modifier_facture, supprimer_facture, ajouter_paiement, liste_paiements, rechercher_factures
from services.fournisseur_service import liste_fournisseurs
from services.import_service import importer_factures_excel
from services.export_service import exporter_factures_excel, creer_modele_factures_excel


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
        header.pack(fill="x", pady=(0, 12))
        title_box = tb.Frame(header)
        title_box.pack(side="left", fill="x", expand=True)
        tb.Label(title_box, text="Factures & avoirs", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(title_box, text="Consultez, importez et gérez les pièces fournisseurs", bootstyle="secondary").pack(anchor="w", pady=(1, 0))

        actions = tb.Frame(header)
        actions.pack(side="right")
        for text, style, command in [
            ("⬇  Exporter", "success-outline", self.export_excel),
            ("📄  Modèle", "secondary-outline", self.export_template),
            ("⬆  Importer", "info-outline", self.import_excel),
            ("＋  Nouvelle pièce", "success", self.open_add_dialog),
        ]:
            tb.Button(actions, text=text, bootstyle=style, command=command, padding=(10, 7)).pack(side="left", padx=3)

        toolbar = tb.Frame(self.body, padding=(10, 9))
        toolbar.pack(fill="x", pady=(0, 10))
        toolbar.columnconfigure(0, weight=1)
        search_box = tb.Frame(toolbar)
        search_box.grid(row=0, column=0, sticky="ew")
        self.search_var = tk.StringVar()
        tb.Label(search_box, text="🔎", font=("Segoe UI", 11)).pack(side="left", padx=(0, 5))
        tb.Entry(search_box, textvariable=self.search_var).pack(side="left", fill="x", expand=True, ipady=4)
        tb.Label(search_box, text="  Numéro / fournisseur", bootstyle="secondary").pack(side="left", padx=8)
        self.status_var = tk.StringVar(value="Tous les statuts")
        self.status_combo = tb.Combobox(toolbar, textvariable=self.status_var, state="readonly", width=22, values=["Tous les statuts", "Impayée", "Partiellement payée", "Payée"])
        self.status_combo.grid(row=0, column=1, padx=10)
        self.status_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(toolbar, text="↻  Actualiser", bootstyle="secondary-outline", command=self.refresh, padding=(10, 6)).grid(row=0, column=2)

        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "Type", "N°", "Fournisseur", "Date", "Échéance", "Montant", "Payé", "Reste", "Statut"))
        self.table.pack(fill="both", expand=True)
        self.table.bind_double_click(self._edit_selected)

        footer = tb.Frame(self.body, padding=(0, 10, 0, 0))
        footer.pack(fill="x")
        self.count_label = tb.Label(footer, text="0 pièce", font=("Segoe UI", 9, "bold"), bootstyle="secondary")
        self.count_label.pack(side="left")
        buttons = tb.Frame(footer)
        buttons.pack(side="right")
        for text, style, command in [
            ("✎  Modifier", "primary-outline", self._edit_selected),
            ("💰  Paiement", "success", self.open_payment_dialog),
            ("✕  Supprimer", "danger-outline", self._delete_selected),
        ]:
            tb.Button(buttons, text=text, bootstyle=style, command=command, padding=(10, 7)).pack(side="left", padx=3)

    def refresh(self):
        try:
            self.fournisseurs = liste_fournisseurs()
            status = self.status_var.get() if hasattr(self, "status_var") else "Tous les statuts"
            enum_status = None if status == "Tous les statuts" else status
            search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
            self.factures = rechercher_factures(statut=enum_status)
            if search:
                self.factures = [f for f in self.factures if search in str(f.numero).lower() or search in str(getattr(f.fournisseur, "nom", "")).lower()]
        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les pièces.\n\n{exc}")
            return
        rows = []
        for f in self.factures:
            type_piece = getattr(f, "type_piece", "Facture")
            montant = float(f.montant or 0)
            rows.append((f.id, type_piece, f.numero, getattr(f.fournisseur, "nom", "") if f.fournisseur else "", f.date_facture, f.date_echeance,
                         f"{montant:,.2f} DA", f"{float(f.montant_paye or 0):,.2f} DA", f"{float(f.reste or 0):,.2f} DA",
                         getattr(f.statut, "value", f.statut)))
        self.table.load_data(rows)
        self.table.autosize()
        self.count_label.configure(text=f"{len(rows)} pièce{'s' if len(rows) != 1 else ''}")

    def export_excel(self):
        path = filedialog.asksaveasfilename(title="Exporter les factures", defaultextension=".xlsx", filetypes=[("Fichier Excel", "*.xlsx")], initialfile="factures_export.xlsx")
        if not path:
            return
        try:
            exporter_factures_excel(path)
            messagebox.showinfo("Export Excel", f"Export terminé.\n\nFichier : {path}")
        except Exception as exc:
            messagebox.showerror("Export Excel", f"Impossible d'exporter les factures.\n\n{exc}")

    def export_template(self):
        path = filedialog.asksaveasfilename(title="Créer le modèle Excel", defaultextension=".xlsx", filetypes=[("Fichier Excel", "*.xlsx")], initialfile="modele_import_factures.xlsx")
        if not path:
            return
        try:
            creer_modele_factures_excel(path)
            messagebox.showinfo("Modèle Excel", f"Modèle créé.\n\nTu peux le remplir puis utiliser « Importer Excel ».\n\nFichier : {path}")
        except Exception as exc:
            messagebox.showerror("Modèle Excel", f"Impossible de créer le modèle.\n\n{exc}")

    def import_excel(self):
        path = filedialog.askopenfilename(title="Choisir le fichier Excel", filetypes=[("Fichiers Excel", "*.xlsx")])
        if not path:
            return
        if not messagebox.askyesno("Importer les anciennes factures", "Les pièces existantes portant le même numéro seront ignorées.\nLes fournisseurs absents seront créés automatiquement.\n\nContinuer ?"):
            return
        try:
            result = importer_factures_excel(path, self._current_user(), creer_fournisseurs=True)
        except Exception as exc:
            messagebox.showerror("Import Excel", f"Import impossible.\n\n{exc}")
            return
        self.refresh()
        message = f"Import terminé.\n\nFactures importées : {result['imported']}\nDoublons ignorés : {result['skipped']}\nFournisseurs créés : {result['suppliers_created']}\nPaiements historiques : {result['payments_created']}"
        if result["errors"]:
            message += "\n\nDétails :\n" + "\n".join(result["errors"][:15])
            if len(result["errors"]) > 15:
                message += f"\n... et {len(result['errors']) - 15} autre(s)."
        messagebox.showinfo("Import Excel", message)

    def _selected(self):
        values = self.table.get_selected()
        if not values:
            messagebox.showwarning("Sélection", "Sélectionnez une pièce.")
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
        libelle = getattr(facture, "type_piece", "Facture").lower()
        if not messagebox.askyesno("Confirmation", f"Supprimer {libelle} « {facture.numero} » ?"):
            return
        try:
            supprimer_facture(facture.id, self._current_user())
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", f"Suppression impossible.\n\n{exc}")

    def _fournisseur_map(self):
        return {f.nom: f.id for f in self.fournisseurs}

    def open_add_dialog(self):
        self.open_form_dialog(None)

    def open_form_dialog(self, facture):
        dialog = tb.Toplevel(self)
        dialog.title("Modifier la pièce" if facture else "Nouvelle facture / avoir")
        dialog.geometry("600x720")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Modifier la pièce" if facture else "Nouvelle facture / avoir", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 18))
        tb.Label(box, text="Type de pièce *").pack(anchor="w", pady=(0, 3))
        type_var = tk.StringVar(value=getattr(facture, "type_piece", "Facture") if facture else "Facture")
        tb.Combobox(box, textvariable=type_var, state="readonly", values=["Facture", "Avoir"]).pack(fill="x", pady=(0, 8))
        entries = {}
        for label, key, value in [("Numéro *", "numero", getattr(facture, "numero", "")), ("Date (AAAA-MM-JJ) *", "date_facture", getattr(facture, "date_facture", date.today())), ("Date échéance (AAAA-MM-JJ) *", "date_echeance", getattr(facture, "date_echeance", date.today())), ("Montant *", "montant", abs(getattr(facture, "montant", 0)) if facture else ""), ("Commentaire", "commentaire", getattr(facture, "commentaire", "") or "")]:
            tb.Label(box, text=label).pack(anchor="w", pady=(7, 3))
            e = tb.Entry(box); e.insert(0, str(value)); e.pack(fill="x"); entries[key] = e
        tb.Label(box, text="Fournisseur *").pack(anchor="w", pady=(7, 3))
        names = list(self._fournisseur_map().keys()); fournisseur_var = tk.StringVar()
        combo = tb.Combobox(box, textvariable=fournisseur_var, state="readonly", values=names); combo.pack(fill="x")
        if facture and facture.fournisseur: fournisseur_var.set(facture.fournisseur.nom)
        elif names: combo.current(0)
        hint = tb.Label(box, text="", bootstyle="info"); hint.pack(anchor="w", pady=(12, 0))
        def update_hint(*_): hint.configure(text="Avoir : le montant sera déduit de la dette fournisseur et ne pourra pas recevoir de paiement." if type_var.get() == "Avoir" else "Facture : le montant augmente la dette fournisseur et peut recevoir des paiements.")
        type_var.trace_add("write", update_hint); update_hint()
        buttons = tb.Frame(box); buttons.pack(fill="x", pady=(25, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)
        def save():
            numero = entries["numero"].get().strip()
            if not numero or not fournisseur_var.get(): messagebox.showwarning("Validation", "Numéro et fournisseur sont obligatoires.", parent=dialog); return
            try:
                d_facture = datetime.strptime(entries["date_facture"].get().strip(), "%Y-%m-%d").date(); d_echeance = datetime.strptime(entries["date_echeance"].get().strip(), "%Y-%m-%d").date(); montant = float(entries["montant"].get().replace(",", "."))
                if montant <= 0: raise ValueError("Le montant doit être strictement supérieur à zéro.")
                if d_echeance < d_facture: raise ValueError("La date d'échéance ne peut pas être avant la date de facture.")
                fournisseur_id = self._fournisseur_map()[fournisseur_var.get()]
                if facture: modifier_facture(facture.id, fournisseur_id, numero, d_facture, d_echeance, montant, entries["commentaire"].get().strip(), self._current_user(), type_var.get())
                else: ajouter_facture(numero, fournisseur_id, d_facture, d_echeance, montant, entries["commentaire"].get().strip(), self._current_user(), type_var.get())
            except Exception as exc: messagebox.showerror("Erreur", f"Impossible d'enregistrer la pièce.\n\n{exc}", parent=dialog); return
            dialog.destroy(); self.refresh()
        tb.Button(buttons, text="Enregistrer", bootstyle="success", command=save).pack(side="right")

    def open_payment_dialog(self):
        facture = self._selected()
        if not facture: return
        if getattr(facture, "type_piece", "Facture") == "Avoir": messagebox.showinfo("Paiement", "Un avoir diminue la dette fournisseur et ne peut pas recevoir de paiement."); return
        if facture.reste <= 0: messagebox.showinfo("Paiement", "Cette facture est déjà entièrement payée."); return
        dialog = tb.Toplevel(self); dialog.title(f"Paiement — {facture.numero}"); dialog.geometry("500x430"); dialog.resizable(False, False); dialog.transient(self.winfo_toplevel()); dialog.grab_set()
        box = tb.Frame(dialog, padding=25); box.pack(fill="both", expand=True)
        tb.Label(box, text="Enregistrer un paiement", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(box, text=f"Facture : {facture.numero}\nReste à payer : {facture.reste:,.2f} DA", font=("Segoe UI", 11)).pack(anchor="w", pady=15)
        tb.Label(box, text="Montant *").pack(anchor="w", pady=(5, 3)); amount = tb.Entry(box); amount.insert(0, str(facture.reste)); amount.pack(fill="x")
        tb.Label(box, text="Mode de paiement").pack(anchor="w", pady=(10, 3)); mode = tb.Combobox(box, state="readonly", values=["Espèces", "Chèque", "Virement", "Carte", "Autre"]); mode.current(0); mode.pack(fill="x")
        tb.Label(box, text="Référence").pack(anchor="w", pady=(10, 3)); reference = tb.Entry(box); reference.pack(fill="x")
        def save():
            try: ajouter_paiement(facture.id, float(amount.get().replace(",", ".")), mode.get(), reference.get().strip(), self._current_user())
            except Exception as exc: messagebox.showerror("Paiement refusé", str(exc), parent=dialog); return
            dialog.destroy(); self.refresh()
        buttons = tb.Frame(box); buttons.pack(fill="x", pady=25)
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)
        tb.Button(buttons, text="Enregistrer le paiement", bootstyle="success", command=save).pack(side="right")

    def show_payments(self):
        facture = self._selected()
        if not facture: return
        paiements = liste_paiements(facture.id)
        if not paiements: messagebox.showinfo("Paiements", "Aucun paiement enregistré."); return
        details = "\n".join(f"{p.date_paiement} — {p.montant:,.2f} DA — {p.mode_paiement or '-'} — {p.reference or '-'}" for p in paiements)
        messagebox.showinfo(f"Paiements — {facture.numero}", details)
