import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime


class TopBar(tb.Frame):

    def __init__(self, master, app):

        super().__init__(
            master,
            bootstyle="light",
            padding=(20, 10)
        )

        self.app = app

        self.columnconfigure(1, weight=1)

        self.build()

        self.update_clock()

    # =====================================================
    # CONSTRUCTION
    # =====================================================

    def build(self):

        # -----------------------
        # TITRE
        # -----------------------

        self.lbl_title = tb.Label(
            self,
            text="Tableau de bord",
            font=("Segoe UI", 18, "bold")
        )

        self.lbl_title.grid(
            row=0,
            column=0,
            sticky="w"
        )

        # -----------------------
        # ESPACE
        # -----------------------

        spacer = tb.Frame(self)

        spacer.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        # -----------------------
        # NOTIFICATIONS
        # -----------------------

        self.btn_notifications = tb.Button(
            self,
            text="🔔 0",
            bootstyle="info-outline",
            width=8,
            command=self.show_notifications
        )

        self.btn_notifications.grid(
            row=0,
            column=2,
            padx=5
        )

        # -----------------------
        # UTILISATEUR
        # -----------------------

        self.lbl_user = tb.Label(
            self,
            text="Invité",
            font=("Segoe UI", 11, "bold")
        )

        self.lbl_user.grid(
            row=0,
            column=3,
            padx=15
        )

        # -----------------------
        # DATE / HEURE
        # -----------------------

        self.lbl_clock = tb.Label(
            self,
            text="",
            font=("Segoe UI", 10)
        )

        self.lbl_clock.grid(
            row=0,
            column=4
        )

    # =====================================================
    # HORLOGE
    # =====================================================

    def update_clock(self):

        now = datetime.now()

        self.lbl_clock.configure(

            text=now.strftime("%d/%m/%Y   %H:%M:%S")

        )

        self.after(
            1000,
            self.update_clock
        )

    # =====================================================
    # UTILISATEUR
    # =====================================================

    def refresh_user(self, user):

        if user is None:

            self.lbl_user.configure(
                text="Invité"
            )

            return

        self.lbl_user.configure(

            text=f"👤 {user.username}"

        )

    # =====================================================
    # TITRE PAGE
    # =====================================================

    def set_page_title(self, titre):

        self.lbl_title.configure(

            text=titre

        )

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    def set_notification_count(self, nombre):

        self.btn_notifications.configure(

            text=f"🔔 {nombre}"

        )

    # =====================================================
    # EVENEMENTS
    # =====================================================

    def show_notifications(self):

        tb.dialogs.Messagebox.show_info(

            "Le centre de notifications sera disponible dans une prochaine version.",

            "Notifications"

        )