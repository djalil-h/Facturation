import ttkbootstrap as tb
from ttkbootstrap.constants import *


class Sidebar(tb.Frame):

    def __init__(self, master):

        super().__init__(
            master,
            width=260,
            bootstyle="light"
        )

        self.master = master

        self.pack_propagate(False)

        self.buttons = {}

        self.build()

    # ==========================================================
    # CONSTRUCTION
    # ==========================================================

    def build(self):

        # -------------------------
        # LOGO
        # -------------------------

        logo = tb.Label(
            self,
            text="⚕",
            font=("Segoe UI Symbol", 38)
        )

        logo.pack(pady=(25, 5))

        hh = tb.Label(
            self,
            text="HH",
            font=("Segoe UI", 24, "bold")
        )

        hh.pack()

        titre = tb.Label(
            self,
            text="Facturation",
            font=("Segoe UI", 16, "bold")
        )

        titre.pack(pady=(10, 0))

        pharmacie = tb.Label(
            self,
            text="Pharmacie\nHamzaoui Hamid",
            justify="center",
            font=("Segoe UI", 10)
        )

        pharmacie.pack(pady=(0, 20))

        ttk_separator = tb.Separator(self)

        ttk_separator.pack(fill="x", padx=15, pady=5)

        # -------------------------
        # MENUS
        # -------------------------

        self.add_button(
            "dashboard",
            "🏠 Tableau de bord",
            self.master.show_dashboard
        )

        self.add_button(
            "fournisseurs",
            "📦 Fournisseurs",
            self.master.show_fournisseurs
        )

        self.add_button(
            "factures",
            "🧾 Factures",
            self.master.show_factures
        )

        self.add_button(
            "paiements",
            "💳 Paiements",
            self.master.show_paiements
        )

        self.add_button(
            "historique",
            "📜 Historique",
            self.master.show_historique
        )

        self.add_button(
            "utilisateurs",
            "👥 Utilisateurs",
            self.master.show_utilisateurs
        )

        self.add_button(
            "journal",
            "🛡 Journal",
            self.master.show_journal
        )

        self.add_button(
            "parametres",
            "⚙ Paramètres",
            self.master.show_parametres
        )

        # espace

        tb.Frame(self).pack(expand=True, fill="both")

        tb.Separator(self).pack(fill="x", padx=15)

        # -------------------------
        # UTILISATEUR
        # -------------------------

        self.lbl_user = tb.Label(
            self,
            text="Utilisateur : Invité",
            font=("Segoe UI", 10)
        )

        self.lbl_user.pack(pady=(15, 5))

        self.lbl_version = tb.Label(
            self,
            text="Version 2.0",
            font=("Segoe UI", 9)
        )

        self.lbl_version.pack()

        tb.Button(
            self,
            text="Déconnexion",
            bootstyle="danger-outline",
            command=self.logout
        ).pack(
            fill="x",
            padx=15,
            pady=15
        )

    # ==========================================================
    # AJOUT D'UN BOUTON
    # ==========================================================

    def add_button(self, key, text, command):

        btn = tb.Button(
            self,
            text=text,
            command=command,
            bootstyle="light",
            width=25
        )

        btn.pack(
            fill="x",
            padx=12,
            pady=4
        )

        self.buttons[key] = btn

    # ==========================================================
    # MENU ACTIF
    # ==========================================================

    def select_menu(self, selected):

        for key, button in self.buttons.items():

            if key == selected:

                button.configure(
                    bootstyle="primary"
                )

            else:

                button.configure(
                    bootstyle="light"
                )

    # ==========================================================
    # UTILISATEUR
    # ==========================================================

    def set_user(self, username):

        self.lbl_user.configure(
            text=f"Utilisateur : {username}"
        )

    # ==========================================================
    # DECONNEXION
    # ==========================================================

    def logout(self):

        from tkinter import messagebox

        if messagebox.askyesno(
            "Déconnexion",
            "Voulez-vous vous déconnecter ?"
        ):

            self.master.destroy()