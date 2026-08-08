import ttkbootstrap as tb

from UI.widgets.brand_logo import BrandLogo


class Sidebar(tb.Frame):
    """Navigation principale moderne, compacte et lisible."""

    def __init__(self, master):
        super().__init__(master, width=225, bootstyle="dark")
        self.master = master
        self.pack_propagate(False)
        self.buttons = {}
        self.build()

    def build(self):
        BrandLogo(self, width=205, height=125, dark=True, compact=True).pack(fill="x", padx=10, pady=(8, 3))
        tb.Separator(self, bootstyle="secondary").pack(fill="x", padx=14, pady=(0, 10))
        tb.Label(self, text="MENU", font=("Segoe UI", 8, "bold"), bootstyle="secondary-inverse").pack(anchor="w", padx=16, pady=(0, 5))

        menus = [
            ("dashboard", "⌂   Tableau de bord", self.master.show_dashboard),
            ("fournisseurs", "▣   Fournisseurs", self.master.show_fournisseurs),
            ("factures", "▤   Factures & avoirs", self.master.show_factures),
            ("paiements", "€   Paiements", self.master.show_paiements),
            ("historique", "◷   Historique", self.master.show_historique),
            ("utilisateurs", "♙   Utilisateurs", self.master.show_utilisateurs),
            ("journal", "▤   Journal", self.master.show_journal),
            ("parametres", "⚙   Paramètres", self.master.show_parametres),
        ]
        for key, text, command in menus:
            self.add_button(key, text, command)

        tb.Frame(self, bootstyle="dark").pack(expand=True, fill="both")
        tb.Separator(self, bootstyle="secondary").pack(fill="x", padx=14)
        self.lbl_user = tb.Label(self, text="Utilisateur : Invité", font=("Segoe UI", 9, "bold"), bootstyle="inverse-dark")
        self.lbl_user.pack(anchor="w", padx=16, pady=(10, 2))
        self.lbl_version = tb.Label(self, text="Version 2.0", font=("Segoe UI", 8), bootstyle="secondary-inverse")
        self.lbl_version.pack(anchor="w", padx=16, pady=(0, 8))
        self.logout_button = tb.Button(
            self, text="⇥   Déconnexion", bootstyle="danger-outline",
            command=self.logout, padding=(9, 6), width=20
        )
        self.logout_button.pack(fill="x", padx=12, pady=(0, 12))

    def add_button(self, key, text, command):
        btn = tb.Button(
            self,
            text=text,
            command=command,
            bootstyle="dark",
            padding=(10, 7),
            width=22,
            compound="center"
        )
        btn.pack(fill="x", padx=9, pady=1)
        self.buttons[key] = btn

    def select_menu(self, selected):
        for key, button in self.buttons.items():
            button.configure(bootstyle="primary" if key == selected else "dark")

    def set_user(self, username):
        if self.winfo_exists():
            self.lbl_user.configure(text=f"Utilisateur : {username}" if username else "Utilisateur : Invité")

    def logout(self):
        from tkinter import messagebox
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            self.master.logout()
