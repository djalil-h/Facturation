import ttkbootstrap as tb


class Sidebar(tb.Frame):
    def __init__(self, master):
        super().__init__(master, width=260, bootstyle="light")
        self.master = master
        self.pack_propagate(False)
        self.buttons = {}
        self.build()

    def build(self):
        tb.Label(self, text="⚕", font=("Segoe UI Symbol", 38)).pack(pady=(25, 5))
        tb.Label(self, text="HH", font=("Segoe UI", 24, "bold")).pack()
        tb.Label(self, text="Facturation", font=("Segoe UI", 16, "bold")).pack(pady=(10, 0))
        tb.Label(
            self,
            text="Pharmacie\nHamzaoui Hamid",
            justify="center",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 20))

        tb.Separator(self).pack(fill="x", padx=15, pady=5)

        menus = [
            ("dashboard", "🏠 Tableau de bord", self.master.show_dashboard),
            ("fournisseurs", "📦 Fournisseurs", self.master.show_fournisseurs),
            ("factures", "🧾 Factures", self.master.show_factures),
            ("paiements", "💳 Paiements", self.master.show_paiements),
            ("historique", "📜 Historique", self.master.show_historique),
            ("utilisateurs", "👥 Utilisateurs", self.master.show_utilisateurs),
            ("journal", "🛡 Journal", self.master.show_journal),
            ("parametres", "⚙ Paramètres", self.master.show_parametres),
        ]

        for key, text, command in menus:
            self.add_button(key, text, command)

        tb.Frame(self).pack(expand=True, fill="both")
        tb.Separator(self).pack(fill="x", padx=15)

        self.lbl_user = tb.Label(self, text="Utilisateur : Invité", font=("Segoe UI", 10))
        self.lbl_user.pack(pady=(15, 5))

        self.lbl_version = tb.Label(self, text="Version 2.0", font=("Segoe UI", 9))
        self.lbl_version.pack()

        tb.Button(
            self,
            text="Déconnexion",
            bootstyle="danger-outline",
            command=self.logout,
        ).pack(fill="x", padx=15, pady=15)

    def add_button(self, key, text, command):
        btn = tb.Button(
            self,
            text=text,
            command=command,
            bootstyle="light",
            width=25,
        )
        btn.pack(fill="x", padx=12, pady=4)
        self.buttons[key] = btn

    def select_menu(self, selected):
        for key, button in self.buttons.items():
            button.configure(bootstyle="primary" if key == selected else "light")

    def set_user(self, username):
        self.lbl_user.configure(
            text=f"Utilisateur : {username}" if username else "Utilisateur : Invité"
        )

    def logout(self):
        from tkinter import messagebox

        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            self.master.logout()
