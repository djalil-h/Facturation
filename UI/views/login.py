import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb

from services.user_service import login
from UI.widgets.brand_logo import BrandLogo


class LoginView(tb.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=24, bootstyle="light")
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        shell = tb.Frame(self, padding=2, bootstyle="secondary")
        shell.grid(row=0, column=0)
        card = tb.Frame(shell, padding=32, bootstyle="light")
        card.pack(padx=1, pady=1)

        BrandLogo(card, width=310, height=178, dark=False, compact=False).pack(pady=(0, 4))
        tb.Label(card, text="Gestion des factures et règlements fournisseurs", font=("Segoe UI", 9), bootstyle="secondary").pack(pady=(0, 20))

        tb.Label(card, text="Nom d'utilisateur", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(3, 5))
        self.username_var = tk.StringVar()
        self.username_entry = tb.Entry(card, textvariable=self.username_var, width=36)
        self.username_entry.pack(fill="x", ipady=6)

        tb.Label(card, text="Mot de passe", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 5))
        self.password_var = tk.StringVar()
        self.password_entry = tb.Entry(card, textvariable=self.password_var, show="•", width=36)
        self.password_entry.pack(fill="x", ipady=6)

        self.error_label = tb.Label(card, text="", bootstyle="danger", wraplength=330)
        self.error_label.pack(pady=(10, 0))

        tb.Button(
            card, text="Se connecter  →", bootstyle="primary", width=31,
            command=self.authenticate, padding=(10, 8)
        ).pack(pady=(18, 4))

        tb.Label(card, text="Pharmacie Hamzaoui Hamid  •  Version 2.0", font=("Segoe UI", 8), bootstyle="secondary").pack(pady=(10, 0))

        self.password_entry.bind("<Return>", lambda _event: self.authenticate())
        self.username_entry.focus_set()

    def authenticate(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.error_label.configure(text="Veuillez saisir vos identifiants.")
            return

        try:
            user = login(username, password)
        except Exception as exc:
            messagebox.showerror("Connexion", f"Impossible de se connecter.\n\n{exc}", parent=self)
            return

        if user is None:
            self.error_label.configure(text="Nom d'utilisateur ou mot de passe incorrect.")
            self.password_var.set("")
            self.password_entry.focus_set()
            return

        self.app.set_current_user(user)
        self.app.show_main_layout()
