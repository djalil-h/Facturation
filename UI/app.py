import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.sidebar import Sidebar
from UI.topbar import TopBar

# Les vues seront créées ensuite
from UI.dashboard import Dashboard


class FacturationApp(tb.Window):

    def __init__(self):

        super().__init__(themename="flatly")

        # ===============================
        # Fenêtre
        # ===============================

        self.title("Facturation - Pharmacie Hamzaoui Hamid")

        self.geometry("1550x900")

        self.minsize(1400, 800)

        self.configure(bg="#F5F7FA")

        # utilisateur connecté
        self.current_user = None

        # vue courante
        self.current_view = None

        # dictionnaire des vues
        self.views = {}

        # création interface
        self.create_layout()

    # =====================================================
    # LAYOUT
    # =====================================================

    def create_layout(self):

        # Fenêtre découpée en 2 colonnes
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)

        # --------------------------------------
        # SIDEBAR
        # --------------------------------------

        self.sidebar = Sidebar(self)

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        # --------------------------------------
        # CONTENEUR PRINCIPAL
        # --------------------------------------

        self.main_container = tb.Frame(
            self,
            bootstyle="light"
        )

        self.main_container.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main_container.columnconfigure(0, weight=1)

        self.main_container.rowconfigure(1, weight=1)

        # --------------------------------------
        # TOPBAR
        # --------------------------------------

        self.topbar = TopBar(
            self.main_container,
            self
        )

        self.topbar.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        # --------------------------------------
        # CONTENU
        # --------------------------------------

        self.content = tb.Frame(
            self.main_container,
            bootstyle="light"
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        # première page

        self.show_dashboard()

    # =====================================================
    # OUTILS
    # =====================================================

    def clear_content(self):

        for widget in self.content.winfo_children():

            widget.destroy()
    # =====================================================
    # NAVIGATION
    # =====================================================

    def show_view(self, view_class):

        """
        Affiche une vue dans la zone centrale.
        """

        self.clear_content()

        self.current_view = view_class(self.content)

        self.current_view.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    # =====================================================
    # PAGES
    # =====================================================

    def show_dashboard(self):

      from UI.dashboard import Dashboard

      self.show_view(Dashboard)

      self.topbar.set_page_title("Tableau de bord")

      self.sidebar.select_menu("dashboard")

    def show_fournisseurs(self):

       from UI.fournisseurs import FournisseursView

       self.show_view(FournisseursView)

       self.topbar.set_page_title("Fournisseurs")

       self.sidebar.select_menu("fournisseurs")

    def show_factures(self):

        from UI.factures import FacturesView

        self.show_view(FacturesView)

        if hasattr(self.sidebar, "select_menu"):
            self.sidebar.select_menu("factures")

    def show_paiements(self):

        from UI.paiements import PaiementsView

        self.show_view(PaiementsView)

        if hasattr(self.sidebar, "select_menu"):
            self.sidebar.select_menu("paiements")

    def show_historique(self):

        from UI.historique import HistoriqueView

        self.show_view(HistoriqueView)

        if hasattr(self.sidebar, "select_menu"):
            self.sidebar.select_menu("historique")

    def show_utilisateurs(self):

        from UI.utilisateurs import UtilisateursView

        self.show_view(UtilisateursView)

        if hasattr(self.sidebar, "select_menu"):
            self.sidebar.select_menu("utilisateurs")

    def show_journal(self):

        from UI.journal import JournalView

        self.show_view(JournalView)

        if hasattr(self.sidebar, "select_menu"):
            self.sidebar.select_menu("journal")

    def show_parametres(self):

        from UI.parametres import ParametresView

        self.show_view(ParametresView)

        if hasattr(self.sidebar, "select_menu"):
            self.sidebar.select_menu("parametres")

    # =====================================================
    # UTILISATEUR
    # =====================================================

    def set_current_user(self, user):

        self.current_user = user

        if hasattr(self.topbar, "refresh_user"):

            self.topbar.refresh_user(user)

    def get_current_user(self):

        return self.current_user
    # =====================================================
    # RAFRAÎCHISSEMENT
    # =====================================================

    def refresh_current_view(self):

        if self.current_view is None:
            return

        if hasattr(self.current_view, "refresh"):
            self.current_view.refresh()

    # =====================================================
    # TITRE
    # =====================================================

    def set_title(self, titre):

        self.title(
            f"Facturation - Pharmacie Hamzaoui Hamid | {titre}"
        )

    # =====================================================
    # FERMETURE
    # =====================================================

    def on_close(self):

        # Ici on ajoutera :
        # - sauvegarde automatique
        # - fermeture propre de la base
        # - journal des actions

        self.destroy()