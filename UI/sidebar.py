import ttkbootstrap as tb


class Sidebar(tb.Frame):
    """Navigation principale : lisible, contrastée et adaptée aux écrans PC."""

    def __init__(self, master):
        super().__init__(master, width=245, bootstyle="dark")
        self.master = master
        self.pack_propagate(False)
        self.buttons = {}
        self.build()

    def build(self):
        header = tb.Frame(self, bootstyle="dark")
        header.pack(fill="x", padx=18, pady=(20, 12))

        tb.Label(header, text="⚕", font=("Segoe UI Symbol", 25, "bold"), bootstyle="inverse-dark").pack(side="left")
        brand = tb.Frame(header, bootstyle="dark")
        brand.pack(side="left", padx=(10, 0))
        tb.Label(brand, text="FACTURATION", font=("Segoe UI", 11, "bold"), bootstyle="inverse-dark").pack(anchor="w")
        tb.Label(brand, text="Pharmacie Hamzaoui Hamid", font=("Segoe UI", 8), bootstyle="secondary-inverse").pack(anchor="w")

        tb.Separator(self, bootstyle="secondary").pack(fill="x", padx=16, pady=(0, 12))
        tb.Label(self, text="MENU PRINCIPAL", font=("Segoe UI", 8, "bold"), bootstyle="secondary-inverse").pack(anchor="w", padx=18, pady=(0, 6))

        menus = [
            ("dashboard", "⌂  Tableau de bord", self.master.show_dashboard),
            ("fournisseurs", "▣  Fournisseurs", self.master.show_fournisseurs),
            ("factures", "▤  Factures", self.master.show_factures),
            ("paiements", "€  Paiements", self.master.show_paiements),
            ("historique", "◷  Historique", self.master.show_historique),
            ("utilisateurs", "♙  Utilisateurs", self.master.show_utilisateurs),
            ("journal", "▤  Journal", self.master.show_journal),
            ("parametres", "⚙  Paramètres", self.master.show_parametres),
        ]
        for key, text, command in menus:
            self.add_button(key, text, command)

        tb.Frame(self, bootstyle="dark").pack(expand=True, fill="both")
        tb.Separator(self, bootstyle="secondary").pack(fill="x", padx=16)

        self.lbl_user = tb.Label(self, text="Utilisateur : Invité", font=("Segoe UI", 9, "bold"), bootstyle="inverse-dark")
        self.lbl_user.pack(anchor="w", padx=18, pady=(12, 2))
        self.lbl_version = tb.Label(self, text="Version 2.0", font=("Segoe UI", 8), bootstyle="secondary-inverse")
        self.lbl_version.pack(anchor="w", padx=18, pady=(0, 10))

        tb.Button(self, text="⇥  Déconnexion", bootstyle="danger-outline", command=self.logout, padding=(10, 7)).pack(fill="x", padx=14, pady=(0, 14))

    def add_button(self, key, text, command):
        btn = tb.Button(self, text=text, command=command, bootstyle="dark", padding=(11, 8), width=22)
        btn.pack(fill="x", padx=10, pady=2)
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
