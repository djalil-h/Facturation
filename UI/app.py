import ttkbootstrap as tb

from UI.sidebar import Sidebar
from UI.topbar import TopBar
from UI.views.login import LoginView


class FacturationApp(tb.Window):
    """Fenêtre principale de l'application de facturation."""

    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Facturation - Pharmacie Hamzaoui Hamid")
        self.geometry("1550x900")
        self.minsize(1200, 750)
        self.configure(bg="#F5F7FA")
        self.current_user = None
        self.current_view = None
        self.main_container = None
        self.content = None
        self.topbar = None
        self.sidebar = None
        self.show_login()

    def clear_root(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_root()
        self.current_view = None
        self.main_container = None
        self.content = None
        self.topbar = None
        self.sidebar = None
        login_view = LoginView(self, self)
        login_view.pack(fill="both", expand=True)

    def show_main_layout(self):
        self.clear_root()
        self.create_layout()
        self.show_dashboard()

    def create_layout(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        # set_current_user() est appelé avant la création de la Sidebar pendant
        # la connexion ; il faut donc synchroniser l'utilisateur ici aussi.
        self.sidebar.set_user(self.current_user.username if self.current_user else None)

        self.main_container = tb.Frame(self, bootstyle="light")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)

        self.topbar = TopBar(self.main_container, self)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.refresh_user(self.current_user)

        self.content = tb.Frame(self.main_container, bootstyle="light")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_view(self, view_class, title, menu_key):
        self.clear_content()
        self.current_view = view_class(self.content)
        self.current_view.grid(row=0, column=0, sticky="nsew")
        self.topbar.set_page_title(title)
        self.set_title(title)
        self.sidebar.select_menu(menu_key)

    def show_dashboard(self):
        from UI.views.dashboard import Dashboard
        self.show_view(Dashboard, "Tableau de bord", "dashboard")

    def show_fournisseurs(self):
        from UI.views.fournisseurs import FournisseursView
        self.show_view(FournisseursView, "Fournisseurs", "fournisseurs")

    def show_factures(self):
        from UI.views.factures import FacturesView
        self.show_view(FacturesView, "Factures", "factures")

    def show_paiements(self):
        from UI.views.paiements import PaiementsView
        self.show_view(PaiementsView, "Paiements", "paiements")

    def show_historique(self):
        from UI.views.historique import HistoriqueView
        self.show_view(HistoriqueView, "Historique", "historique")

    def show_utilisateurs(self):
        from UI.views.utilisateurs import UtilisateursView
        self.show_view(UtilisateursView, "Utilisateurs", "utilisateurs")

    def show_journal(self):
        from UI.views.journal import JournalView
        self.show_view(JournalView, "Journal", "journal")

    def show_parametres(self):
        from UI.views.parametres import ParametresView
        self.show_view(ParametresView, "Paramètres", "parametres")

    def set_current_user(self, user):
        self.current_user = user
        if self.topbar is not None and self.topbar.winfo_exists():
            self.topbar.refresh_user(user)
        if self.sidebar is not None and self.sidebar.winfo_exists():
            self.sidebar.set_user(user.username if user else None)

    def get_current_user(self):
        return self.current_user

    def refresh_current_view(self):
        if self.current_view is not None and hasattr(self.current_view, "refresh"):
            self.current_view.refresh()

    def set_title(self, titre):
        self.title(f"Facturation - Pharmacie Hamzaoui Hamid | {titre}")

    def logout(self):
        self.current_user = None
        self.show_login()

    def on_close(self):
        self.destroy()
