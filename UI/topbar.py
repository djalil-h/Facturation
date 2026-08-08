import ttkbootstrap as tb
from datetime import datetime


class TopBar(tb.Frame):
    """Barre supérieure moderne, claire et compacte."""

    def __init__(self, master, app):
        super().__init__(master, bootstyle="light", padding=(18, 10))
        self.app = app
        self.columnconfigure(1, weight=1)
        self.build()
        self.update_clock()

    def build(self):
        title_box = tb.Frame(self, bootstyle="light")
        title_box.grid(row=0, column=0, sticky="w")
        self.lbl_title = tb.Label(title_box, text="Tableau de bord", font=("Segoe UI", 17, "bold"), bootstyle="dark")
        self.lbl_title.pack(anchor="w")
        self.lbl_subtitle = tb.Label(title_box, text="Gestion des factures et règlements fournisseurs", font=("Segoe UI", 8), bootstyle="secondary")
        self.lbl_subtitle.pack(anchor="w", pady=(1, 0))

        tb.Frame(self, bootstyle="light").grid(row=0, column=1, sticky="ew")

        self.btn_notifications = tb.Button(self, text="🔔  0", bootstyle="info-outline", padding=(9, 6), command=self.show_notifications)
        self.btn_notifications.grid(row=0, column=2, padx=(8, 10))

        user_box = tb.Frame(self, bootstyle="light", padding=(8, 2))
        user_box.grid(row=0, column=3, padx=(0, 4))
        self.lbl_user = tb.Label(user_box, text="👤  Invité", font=("Segoe UI", 9, "bold"), bootstyle="dark")
        self.lbl_user.pack(anchor="e")
        self.lbl_clock = tb.Label(user_box, text="", font=("Segoe UI", 8), bootstyle="secondary")
        self.lbl_clock.pack(anchor="e", pady=(1, 0))

    def update_clock(self):
        if not self.winfo_exists():
            return
        self.lbl_clock.configure(text=datetime.now().strftime("%d/%m/%Y  •  %H:%M:%S"))
        self.after(1000, self.update_clock)

    def refresh_user(self, user):
        if not self.winfo_exists():
            return
        self.lbl_user.configure(text=f"👤  {user.username}" if user else "👤  Invité")

    def set_page_title(self, titre):
        if self.winfo_exists():
            self.lbl_title.configure(text=titre)

    def set_notification_count(self, nombre):
        if self.winfo_exists():
            self.btn_notifications.configure(text=f"🔔  {nombre}")

    def show_notifications(self):
        tb.dialogs.Messagebox.show_info("Le centre de notifications sera disponible dans une prochaine version.", "Notifications")
