import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.facture_service import (
    liste_factures,
    ajouter_paiement,
    liste_paiements,
    regler_plusieurs_factures,
)


class PaiementsView(BaseView):
    """Vue globale des paiements enregistrés."""

    def __init__(self, master):
        super().__init__(master, "Gestion des paiements")
        self.factures = []
        self.paiements = []
        self._build()
        self.refresh()

    def _current_user(self):
        return self.winfo_toplevel().get_current_user()

    def _build(self):
        header = tb.Frame(self.body)
        header.pack(fill="x", pady=(0, 15))
        tb.Label(header, text="Paiements", font=("Segoe UI", 22, "bold")).pack(side="left")

        actions = tb.Frame(header)
        actions.pack(side="right")
        tb.Button(actions, text="☑ Régler plusieurs factures", bootstyle="warning", command=self.open_bulk_payment_dialog).pack(side="left", padx=(0, 8))
        tb.Button(actions, text="＋ Nouveau paiement", bootstyle="success", command=self.open_payment_dialog).pack(side="left")

        toolbar = tb.Frame(self.body)
        toolbar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        tb.Entry(toolbar, textvariable=self.search_var, width=40).pack(side="left", ipady=5)
        tb.Label(toolbar, text="  Facture / référence").pack(side="left")
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(toolbar, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh).pack(side="right")

        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "Facture", "Date", "Montant", "Mode", "Référence"))
        self.table.pack(fill="both", expand=True)

        footer = tb.Frame(self.body)
        footer.pack(fill="x", pady=(12, 0))
        self.total_label = tb.Label(footer, text="Total : 0.00 DA")
        self.total_label.pack(side="left")

    def refresh(self):
        try:
            self.factures = liste_factures()
            self.paiements = []
            for facture in self.factures:
                for paiement in liste_paiements(facture.id):
                    paiement._facture_numero = facture.numero
                    self.paiements.append(paiement)
        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les paiements.\n\n{exc}")
            return

        search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        rows = []
        total = 0
        for p in self.paiements:
            facture_numero = getattr(p, "_facture_numero", "")
            if search and search not in facture_numero.lower() and search not in str(p.reference or "").lower():
                continue
            total += p.montant
            rows.append((p.id, facture_numero, p.date_paiement, f"{p.montant:,.2f} DA", p.mode_paiement or "", p.reference or ""))

        self.table.load_data(rows)
        self.table.autosize()
        self.total_label.configure(text=f"Total : {total:,.2f} DA")

    def open_payment_dialog(self):
        if not self.factures:
            messagebox.showwarning("Paiement", "Aucune facture disponible.")
            return

        dialog = tb.Toplevel(self)
        dialog.title("Nouveau paiement")
        dialog.geometry("520x450")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Nouveau paiement", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 18))

        tb.Label(box, text="Facture *").pack(anchor="w", pady=(5, 3))
        facture_var = tk.StringVar()
        factures = [f"{f.numero} — reste {f.reste:,.2f} DA" for f in self.factures if f.reste > 0 and getattr(f, "type_piece", "Facture") != "Avoir"]
        combo = tb.Combobox(box, textvariable=facture_var, state="readonly", values=factures)
        combo.pack(fill="x")
        if factures:
            combo.current(0)

        tb.Label(box, text="Montant *").pack(anchor="w", pady=(10, 3))
        amount = tb.Entry(box)
        amount.pack(fill="x")
        tb.Label(box, text="Mode").pack(anchor="w", pady=(10, 3))
        mode = tb.Combobox(box, state="readonly", values=["Espèces", "Chèque", "Virement", "Carte", "Autre"])
        mode.current(0)
        mode.pack(fill="x")
        tb.Label(box, text="Référence").pack(anchor="w", pady=(10, 3))
        reference = tb.Entry(box)
        reference.pack(fill="x")

        def save():
            if not facture_var.get():
                messagebox.showwarning("Validation", "Sélectionnez une facture.", parent=dialog)
                return
            try:
                numero = facture_var.get().split(" — ", 1)[0]
                facture = next(f for f in self.factures if f.numero == numero)
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
        tb.Button(buttons, text="Enregistrer", bootstyle="success", command=save).pack(side="right")

    def open_bulk_payment_dialog(self, fournisseur_id=None, fournisseur_nom=None):
        """Sélectionne plusieurs factures et, séparément, les avoirs à imputer."""
        pieces = [f for f in self.factures if fournisseur_id is None or getattr(f, "fournisseur_id", None) == fournisseur_id]
        factures = [f for f in pieces if float(f.reste or 0) > 0 and getattr(f, "type_piece", "Facture") != "Avoir"]
        avoirs = [f for f in pieces if getattr(f, "type_piece", "Facture") == "Avoir" and float(f.reste or 0) < 0]

        if not factures:
            messagebox.showinfo("Règlement groupé", f"Aucune facture impayée{f' pour {fournisseur_nom}' if fournisseur_nom else ''}.", parent=self)
            return

        dialog = tb.Toplevel(self)
        dialog.title("Régler les factures" + (f" — {fournisseur_nom}" if fournisseur_nom else ""))
        dialog.geometry("760x720")
        dialog.minsize(680, 600)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        box = tb.Frame(dialog, padding=20)
        box.pack(fill="both", expand=True)
        titre = "Règlement fournisseur"
        if fournisseur_nom:
            titre += f" — {fournisseur_nom}"
        tb.Label(box, text=titre, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(box, text="Cochez les factures à régler et, si nécessaire, les avoirs à imputer. Les avoirs sélectionnés réduisent la dette avant le paiement.", bootstyle="secondary", wraplength=700).pack(anchor="w", pady=(4, 12))

        list_frame = tb.Frame(box)
        list_frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        inner = tb.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))

        facture_selections = {}
        avoir_selections = {}

        tb.Label(inner, text="FACTURES À RÉGLER", font=("Segoe UI", 10, "bold"), bootstyle="primary").pack(fill="x", pady=(2, 6))
        for facture in factures:
            var = tk.BooleanVar(value=False)
            facture_selections[facture.id] = var
            texte = f"☐ {facture.numero}  |  reste : {float(facture.reste):,.2f} DA"
            tb.Checkbutton(inner, text=texte, variable=var, bootstyle="primary").pack(fill="x", anchor="w", pady=4, padx=5)

        if avoirs:
            tb.Separator(inner).pack(fill="x", pady=10)
            tb.Label(inner, text="AVOIRS DISPONIBLES — À IMPUTER", font=("Segoe UI", 10, "bold"), bootstyle="info").pack(fill="x", pady=(2, 6))
            for avoir in avoirs:
                var = tk.BooleanVar(value=False)
                avoir_selections[avoir.id] = var
                texte = f"↩ {avoir.numero}  |  crédit disponible : {abs(float(avoir.reste)):,.2f} DA"
                tb.Checkbutton(inner, text=texte, variable=var, bootstyle="info").pack(fill="x", anchor="w", pady=4, padx=5)
        else:
            tb.Label(inner, text="Aucun avoir disponible pour ce fournisseur.", bootstyle="secondary").pack(anchor="w", pady=(8, 4), padx=5)

        total_var = tk.StringVar(value="Factures sélectionnées : 0.00 DA    •    Avoirs sélectionnés : 0.00 DA    •    Paiement prévu : 0.00 DA")
        tb.Label(box, textvariable=total_var, font=("Segoe UI", 11, "bold"), wraplength=700).pack(anchor="w", pady=(10, 8))

        def update_total(*_):
            total_factures = sum(float(f.reste or 0) for f in factures if facture_selections[f.id].get())
            total_avoirs = sum(abs(float(a.reste or 0)) for a in avoirs if avoir_selections[a.id].get())
            total_avoirs_utilisable = min(total_factures, total_avoirs)
            paiement = max(0.0, total_factures - total_avoirs_utilisable)
            total_var.set(f"Factures sélectionnées : {total_factures:,.2f} DA    •    Avoirs sélectionnés : {total_avoirs:,.2f} DA    •    Paiement prévu : {paiement:,.2f} DA")

        for var in list(facture_selections.values()) + list(avoir_selections.values()):
            var.trace_add("write", update_total)

        form = tb.Frame(box)
        form.pack(fill="x", pady=(4, 8))
        tb.Label(form, text="Mode").grid(row=0, column=0, sticky="w", padx=(0, 8))
        mode = tb.Combobox(form, state="readonly", values=["Espèces", "Chèque", "Virement", "Carte", "Autre"], width=18)
        mode.current(0)
        mode.grid(row=0, column=1, sticky="w", padx=(0, 25))
        tb.Label(form, text="Référence").grid(row=0, column=2, sticky="w", padx=(0, 8))
        reference = tb.Entry(form, width=25)
        reference.grid(row=0, column=3, sticky="ew")
        form.columnconfigure(3, weight=1)

        def save():
            facture_ids = [fid for fid, var in facture_selections.items() if var.get()]
            avoir_ids = [aid for aid, var in avoir_selections.items() if var.get()]
            if not facture_ids:
                messagebox.showwarning("Validation", "Sélectionnez au moins une facture.", parent=dialog)
                return
            try:
                result = regler_plusieurs_factures(facture_ids, mode.get(), reference.get().strip(), self._current_user(), avoir_ids=avoir_ids)
            except Exception as exc:
                messagebox.showerror("Règlement refusé", str(exc), parent=dialog)
                return
            dialog.destroy()
            self.refresh()
            details = f"{result['factures']} facture(s) traitée(s).\n\nPaiement effectué : {result['total']:,.2f} DA"
            if result.get("avoir_impute", 0) > 0:
                details += f"\nAvoir imputé : {result['avoir_impute']:,.2f} DA"
            messagebox.showinfo("Règlement effectué", details, parent=self)

        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=(12, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)
        tb.Button(buttons, text="Régler les factures sélectionnées", bootstyle="success", command=save).pack(side="right")
