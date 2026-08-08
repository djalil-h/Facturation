import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.user_service import get_users, create_user, update_user, delete_user, disable_user, enable_user


class UtilisateursView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Utilisateurs")
        self.users = []
        self._build()
        self.refresh()

    def _build(self):
        header = tb.Frame(self.body)
        header.pack(fill="x", pady=(0, 15))
        tb.Label(header, text="Utilisateurs", font=("Segoe UI", 22, "bold")).pack(side="left")
        tb.Button(header, text="＋ Nouvel utilisateur", bootstyle="success", command=self.open_add_dialog).pack(side="right")

        bar = tb.Frame(self.body)
        bar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        tb.Entry(bar, textvariable=self.search_var, width=40).pack(side="left", ipady=5)
        tb.Label(bar, text="  Rechercher un utilisateur").pack(side="left")
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(bar, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh).pack(side="right")

        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "Utilisateur", "Rôle", "Statut", "Créé le", "Dernière connexion"))
        self.table.pack(fill="both", expand=True)
        self.table.bind_double_click(self._edit_selected)

        footer = tb.Frame(self.body)
        footer.pack(fill="x", pady=(12, 0))
        self.count_label = tb.Label(footer, text="0 utilisateur")
        self.count_label.pack(side="left")
        tb.Button(footer, text="✎ Modifier", bootstyle="primary-outline", command=self._edit_selected).pack(side="right", padx=4)
        tb.Button(footer, text="Activer / Désactiver", bootstyle="warning-outline", command=self._toggle_selected).pack(side="right", padx=4)
        tb.Button(footer, text="✕ Supprimer", bootstyle="danger-outline", command=self._delete_selected).pack(side="right", padx=4)

    def refresh(self):
        try:
            self.users = get_users()
        except Exception as exc:
            messagebox.showerror("Utilisateurs", f"Impossible de charger les utilisateurs.\n\n{exc}")
            return
        search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        rows = []
        for user in self.users:
            values = (
                user.id,
                user.username,
                user.role,
                "Actif" if user.is_active else "Désactivé",
                str(user.created_at or ""),
                str(user.last_login or "Jamais"),
            )
            if search and not any(search in str(v).lower() for v in values):
                continue
            rows.append(values)
        self.table.load_data(rows)
        self.table.autosize()
        self.count_label.configure(text=f"{len(rows)} utilisateur{'s' if len(rows) != 1 else ''}")

    def _selected(self):
        values = self.table.get_selected()
        if not values:
            messagebox.showwarning("Sélection", "Sélectionnez un utilisateur.")
            return None
        return next((u for u in self.users if u.id == int(values[0])), None)

    def _edit_selected(self, _event=None):
        user = self._selected()
        if user:
            self.open_form_dialog(user)

    def _delete_selected(self):
        user = self._selected()
        if not user:
            return
        if not messagebox.askyesno("Confirmation", f"Supprimer l'utilisateur « {user.username} » ?"):
            return
        try:
            delete_user(user.id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Suppression", str(exc))

    def _toggle_selected(self):
        user = self._selected()
        if not user:
            return
        try:
            if user.is_active:
                disable_user(user.id)
            else:
                enable_user(user.id)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Statut", str(exc))

    def open_add_dialog(self):
        self.open_form_dialog(None)

    def open_form_dialog(self, user):
        dialog = tb.Toplevel(self)
        dialog.title("Modifier l'utilisateur" if user else "Nouvel utilisateur")
        dialog.geometry("520x430")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Modifier l'utilisateur" if user else "Nouvel utilisateur", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 18))

        tb.Label(box, text="Nom d'utilisateur *").pack(anchor="w", pady=(5, 3))
        username = tb.Entry(box)
        username.insert(0, user.username if user else "")
        username.pack(fill="x")

        tb.Label(box, text="Rôle *").pack(anchor="w", pady=(10, 3))
        role = tb.Combobox(box, state="readonly", values=["ADMIN", "USER"])
        role.set(user.role if user else "USER")
        role.pack(fill="x")

        tb.Label(box, text="Mot de passe" + (" *" if not user else " (laisser vide pour conserver)" )).pack(anchor="w", pady=(10, 3))
        password = tb.Entry(box, show="•")
        password.pack(fill="x")

        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=25)
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)

        def save():
            try:
                if user:
                    update_user(user.id, username.get().strip(), role.get(), password.get())
                else:
                    create_user(username.get(), password.get(), role.get())
            except Exception as exc:
                messagebox.showerror("Utilisateur", str(exc), parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        tb.Button(buttons, text="Enregistrer", bootstyle="success", command=save).pack(side="right")
