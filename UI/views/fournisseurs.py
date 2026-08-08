import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.fournisseur_service import (
    ajouter_fournisseur,
    liste_fournisseurs,
    rechercher_fournisseur,
    modifier_fournisseur,
    supprimer_fournisseur,
)


class FournisseursView(BaseView):
    """Gestion complète des fournisseurs."""

    def __init__(self, master):
        super().__init__(master, "Gestion des fournisseurs")
        self.fournisseurs = []
        self._build()
        self.refresh()

    def _build(self):
        header = tb.Frame(self.body)
        header.pack(fill="x", pady=(0, 15))

        tb.Label(
            header,
            text="Fournisseurs",
            font=("Segoe UI", 22, "bold"),
        ).pack(side="left")

        tb.Button(
            header,
            text="＋ Ajouter un fournisseur",
            bootstyle="success",
            command=self.open_add_dialog,
        ).pack(side="right")

        toolbar = tb.Frame(self.body)
        toolbar.pack(fill="x", pady=(0, 12))

        self.search_var = tk.StringVar()
        search = tb.Entry(
            toolbar,
            textvariable=self.search_var,
            width=45,
        )
        search.pack(side="left", ipady=5)
        search.insert(0, "")
        search.bind("<KeyRelease>", lambda _event: self.refresh())

        tb.Label(toolbar, text="  Rechercher par nom").pack(side="left")

        tb.Button(
            toolbar,
            text="↻ Actualiser",
            bootstyle="secondary-outline",
            command=self.refresh,
        ).pack(side="right")

        table_frame = tb.Frame(self.body)
        table_frame.pack(fill="both", expand=True)

        self.table = ModernTable(
            table_frame,
            ("ID", "Nom", "Contact", "Téléphone", "Email", "Ville", "Actions"),
        )
        self.table.pack(fill="both", expand=True)
        self.table.bind_double_click(self._edit_selected)

        footer = tb.Frame(self.body)
        footer.pack(fill="x", pady=(12, 0))

        self.count_label = tb.Label(footer, text="0 fournisseur")
        self.count_label.pack(side="left")

        tb.Button(
            footer,
            text="✎ Modifier",
            bootstyle="primary-outline",
            command=self._edit_selected,
        ).pack(side="right", padx=4)
        tb.Button(
            footer,
            text="✕ Supprimer",
            bootstyle="danger-outline",
            command=self._delete_selected,
        ).pack(side="right", padx=4)

    def refresh(self):
        search = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        try:
            if search:
                self.fournisseurs = rechercher_fournisseur(search)
            else:
                self.fournisseurs = liste_fournisseurs()
        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les fournisseurs.\n\n{exc}")
            return

        rows = []
        for fournisseur in self.fournisseurs:
            rows.append((
                fournisseur.id,
                fournisseur.nom or "",
                fournisseur.contact or "",
                fournisseur.telephone or "",
                fournisseur.email or "",
                fournisseur.ville or "",
                "Double-clic",
            ))

        self.table.load_data(rows)
        self.table.autosize()
        total = len(rows)
        self.count_label.configure(text=f"{total} fournisseur{'s' if total != 1 else ''}")

    def _selected_id(self):
        values = self.table.get_selected()
        if not values:
            messagebox.showwarning("Sélection", "Sélectionnez d'abord un fournisseur.")
            return None
        try:
            return int(values[0])
        except (TypeError, ValueError):
            messagebox.showerror("Erreur", "Le fournisseur sélectionné est invalide.")
            return None

    def _edit_selected(self, _event=None):
        fournisseur_id = self._selected_id()
        if fournisseur_id is None:
            return
        fournisseur = next((f for f in self.fournisseurs if f.id == fournisseur_id), None)
        if fournisseur:
            self.open_form_dialog(fournisseur)

    def _delete_selected(self):
        fournisseur_id = self._selected_id()
        if fournisseur_id is None:
            return
        fournisseur = next((f for f in self.fournisseurs if f.id == fournisseur_id), None)
        if not fournisseur:
            return

        if not messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer le fournisseur « {fournisseur.nom} » ?",
        ):
            return

        try:
            supprimer_fournisseur(fournisseur_id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Suppression impossible",
                "Le fournisseur ne peut peut-être pas être supprimé car il est utilisé par des factures.\n\n"
                f"Détail : {exc}",
            )

    def open_add_dialog(self):
        self.open_form_dialog(None)

    def open_form_dialog(self, fournisseur):
        dialog = tb.Toplevel(self)
        dialog.title("Modifier le fournisseur" if fournisseur else "Ajouter un fournisseur")
        dialog.geometry("560x560")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        container = tb.Frame(dialog, padding=25)
        container.pack(fill="both", expand=True)

        title = "Modifier le fournisseur" if fournisseur else "Nouveau fournisseur"
        tb.Label(container, text=title, font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 20))

        fields = [
            ("Nom *", "nom"),
            ("Contact", "contact"),
            ("Téléphone", "telephone"),
            ("Email", "email"),
            ("Adresse", "adresse"),
            ("Ville", "ville"),
        ]

        entries = {}
        for label, key in fields:
            tb.Label(container, text=label).pack(anchor="w", pady=(7, 3))
            entry = tb.Entry(container)
            entry.pack(fill="x")
            entries[key] = entry

        if fournisseur:
            for _, key in fields:
                entries[key].insert(0, getattr(fournisseur, key, "") or "")

        buttons = tb.Frame(container)
        buttons.pack(fill="x", pady=(25, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=(8, 0))

        def save():
            nom = entries["nom"].get().strip()
            if not nom:
                messagebox.showwarning("Validation", "Le nom du fournisseur est obligatoire.", parent=dialog)
                entries["nom"].focus_set()
                return

            values = {
                key: entries[key].get().strip()
                for _, key in fields
            }

            try:
                if fournisseur:
                    modifier_fournisseur(fournisseur.id, **values)
                else:
                    ajouter_fournisseur(**values)
            except Exception as exc:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer le fournisseur.\n\n{exc}", parent=dialog)
                return

            dialog.destroy()
            self.refresh()

        tb.Button(
            buttons,
            text="Enregistrer",
            bootstyle="success",
            command=save,
        ).pack(side="right")

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
