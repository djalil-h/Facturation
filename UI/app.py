import ttkbootstrap as tb

from UI.sidebar import Sidebar
from UI.topbar import TopBar


class FacturationApp(tb.Window):
    """Main application window and navigation controller."""

    def __init__(self):
        super().__init__(themename="flatly")

        self.title("Facturation - Pharmacie Hamzaoui Hamid")
        self.geometry("1550x900")
        self.minsize(1400, 800)
        self.configure(bg="#F5F7FA")

        self.current_user = None
        self.current_view = None

        self.create_layout()

    def create_layout(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.main_container = tb.Frame(self, bootstyle="light")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)

        self.topbar = TopBar(self.main_container, self)
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.content = tb.Frame(self.main_container, bootstyle="light")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.show_dashboard()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_view(self, view_class):
        self.clear_content()
        self.current_view = view_class(self.content)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def _navigate(self, view_class, title, menu_key):
        self.show_view(view_class)
        self.topbar.set_page_title(title)
        self.set_title(title)
        self.sidebar.select_menu(menu_key)

    def show_dashboard(self):
        from UI.dashboard import Dashboard
        self._navigate(Dashboard, "Tableau de bord", "dashboard")

    def show_fournisseurs(self):
        from UI.fournisseurs import FournisseursView
        self._navigate(FournisseursView, "Fournisseurs", "fournisseurs")

    def show_factures(self):
        from UI.factures import FacturesView
        self._navigate(FacturesView, "Factures", "factures")

    def show_paiements(self):
        from UI.paiements import PaiementsView
        self._navigate(PaiementsView, "Paiements", "paiements")

    def show_historique(self):
        from UI.historique import HistoriqueView
        self._navigate(HistoriqueView, "Historique", "historique")

    def show_utilisateurs(self):
        from UI.utilisateurs import UtilisateursView
        self._navigate(UtilisateursView, "Utilisateurs", "utilisateurs")

    def show_journal(self):
        from UI.journal import JournalView
        self._navigate(JournalView, "Journal administrateur", "journal")

    def show_parametres(self):
        from UI.parametres import ParametresView
        self._navigate(ParametresView, "Paramètres", "parametres")

    def set_current_user(self, user):
        self.current_user = user
        self.topbar.refresh_user(user)
        self.sidebar.set_user(user.username if user else None)

    def get_current_user(self):
        return self.current_user

    def refresh_current_view(self):
        if self.current_view is not None and hasattr(self.current_view, "refresh"):
            self.current_view.refresh()

    def set_title(self, titre):
        self.title(f"Facturation - Pharmacie Hamzaoui Hamid | {titre}")

    def on_close(self):
        self.destroy()
