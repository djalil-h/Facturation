import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.facture_service import liste_factures, ajouter_paiement, liste_paiements


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
        tb.Button(header, text="＋ Nouveau paiement", bootstyle="success", command=self.open_payment_dialog).pack(side="right")

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
