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

        card = tb.Frame(self, padding=28, bootstyle="light")
        card.grid(row=0, column=0)

        BrandLogo(card, width=300, height=180, dark=False, compact=False).pack(pady=(0, 8))
        tb.Label(card, text="Connexion", font=("Segoe UI", 12, "bold"), bootstyle="secondary").pack(pady=(0, 22))

        tb.Label(card, text="Nom d'utilisateur").pack(anchor="w", pady=(5, 4))
        self.username_var = tk.StringVar()
        self.username_entry = tb.Entry(card, textvariable=self.username_var, width=35)
        self.username_entry.pack(ipady=6)

        tb.Label(card, text="Mot de passe").pack(anchor="w", pady=(15, 4))
        self.password_var = tk.StringVar()
        self.password_entry = tb.Entry(card, textvariable=self.password_var, show="•", width=35)
        self.password_entry.pack(ipady=6)

        self.error_label = tb.Label(card, text="", bootstyle="danger")
        self.error_label.pack(pady=(10, 0))

        tb.Button(card, text="Se connecter", bootstyle="primary", width=30,
                  command=self.authenticate).pack(pady=(18, 5), ipady=5)

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
