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
        tb.Button(
            actions,
            text="☑ Régler plusieurs factures",
            bootstyle="warning",
            command=self.open_bulk_payment_dialog,
        ).pack(side="left", padx=(0, 8))
        tb.Button(
            actions,
            text="＋ Nouveau paiement",
            bootstyle="success",
            command=self.open_payment_dialog,
        ).pack(side="left")

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
        factures = [f"{f.numero} — reste {f.reste:,.2f} DA" for f in self.factures if f.reste > 0]
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
        """Règle plusieurs factures, éventuellement limitées à un fournisseur."""
        impayees = [f for f in self.factures if float(f.reste or 0) > 0 and getattr(f, "type_piece", "Facture") != "Avoir"]
        if fournisseur_id is not None:
            impayees = [f for f in impayees if getattr(f, "fournisseur_id", None) == fournisseur_id]

        if not impayees:
            messagebox.showinfo(
                "Règlement groupé",
                f"Aucune facture impayée{f' pour {fournisseur_nom}' if fournisseur_nom else ''}.",
                parent=self,
            )
            return

        dialog = tb.Toplevel(self)
        dialog.title("Régler les factures" + (f" — {fournisseur_nom}" if fournisseur_nom else ""))
        dialog.geometry("720x650")
        dialog.minsize(650, 550)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        box = tb.Frame(dialog, padding=20)
        box.pack(fill="both", expand=True)
        titre = "Régler les factures"
        if fournisseur_nom:
            titre += f" — {fournisseur_nom}"
        tb.Label(box, text=titre, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(
            box,
            text="Sélectionnez les factures à régler. Un paiement sera créé pour chaque facture sélectionnée.",
            bootstyle="secondary",
            wraplength=650,
        ).pack(anchor="w", pady=(4, 15))

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

        selections = {}
        for facture in impayees:
            var = tk.BooleanVar(value=False)
            selections[facture.id] = var
            fournisseur = getattr(getattr(facture, "fournisseur", None), "nom", "Fournisseur inconnu")
            texte = f"{facture.numero}  |  {fournisseur}  |  reste : {float(facture.reste):,.2f} DA"
            tb.Checkbutton(inner, text=texte, variable=var, bootstyle="primary").pack(fill="x", anchor="w", pady=5, padx=5)

        total_var = tk.StringVar(value="Total sélectionné : 0.00 DA")
        tb.Label(box, textvariable=total_var, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 8))

        def update_total(*_):
            total = sum(float(f.reste or 0) for f in impayees if selections[f.id].get())
            total_var.set(f"Total sélectionné : {total:,.2f} DA")

        for var in selections.values():
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
            ids = [facture_id for facture_id, var in selections.items() if var.get()]
            if not ids:
                messagebox.showwarning("Validation", "Sélectionnez au moins une facture.", parent=dialog)
                return
            try:
                result = regler_plusieurs_factures(ids, mode.get(), reference.get().strip(), self._current_user())
            except Exception as exc:
                messagebox.showerror("Règlement refusé", str(exc), parent=dialog)
                return
            dialog.destroy()
            self.refresh()
            messagebox.showinfo(
                "Règlement effectué",
                f"{result['factures']} facture(s) réglée(s).\n\nTotal payé : {result['total']:,.2f} DA",
                parent=self,
            )

        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=(12, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)
        tb.Button(buttons, text="Régler les factures sélectionnées", bootstyle="success", command=save).pack(side="right")
