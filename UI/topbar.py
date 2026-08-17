import tkinter as tk
from datetime import datetime

import ttkbootstrap as tb

from services.dashboard_service import DashboardService


class TopBar(tb.Frame):
    """Barre supérieure moderne avec centre de notifications réel et lisible."""

    def __init__(self, master, app):
        super().__init__(master, bootstyle="light", padding=(18, 11))
        self.app = app
        self._notification_window = None
        self.columnconfigure(1, weight=1)
        self.build()
        self.update_clock()
        self.refresh_notifications()

    def build(self):
        title_box = tb.Frame(self, bootstyle="light")
        title_box.grid(row=0, column=0, sticky="w")
        self.lbl_title = tb.Label(title_box, text="Tableau de bord", font=("Segoe UI", 19, "bold"), bootstyle="dark")
        self.lbl_title.pack(anchor="w")
        self.lbl_subtitle = tb.Label(title_box, text="Gestion des factures et règlements fournisseurs", font=("Segoe UI", 10), bootstyle="secondary")
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        tb.Frame(self, bootstyle="light").grid(row=0, column=1, sticky="ew")

        self.btn_notifications = tb.Button(self, text="🔔  0", bootstyle="info-outline", padding=(11, 8), command=self.show_notifications)
        self.btn_notifications.grid(row=0, column=2, padx=(8, 10))

        user_box = tb.Frame(self, bootstyle="light", padding=(8, 2))
        user_box.grid(row=0, column=3, padx=(0, 4))
        self.lbl_user = tb.Label(user_box, text="👤  Invité", font=("Segoe UI", 10, "bold"), bootstyle="dark")
        self.lbl_user.pack(anchor="e")
        self.lbl_clock = tb.Label(user_box, text="", font=("Segoe UI", 9), bootstyle="secondary")
        self.lbl_clock.pack(anchor="e", pady=(2, 0))

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

    def refresh_notifications(self):
        """Actualise le compteur depuis les données réelles du tableau de bord."""
        if not self.winfo_exists():
            return
        try:
            data = DashboardService.get_dashboard_data()
            self._notification_data = data
            count = int(data.get("retard", 0) or 0) + int(data.get("echeance", 0) or 0)
            self.set_notification_count(count)
        except Exception as exc:
            print("Erreur centre de notifications :", exc)
            self._notification_data = {}
            self.set_notification_count(0)
        self.after(30000, self.refresh_notifications)

    def show_notifications(self):
        if self._notification_window is not None and self._notification_window.winfo_exists():
            self._notification_window.deiconify()
            self._notification_window.lift()
            self._notification_window.focus_force()
            return

        try:
            data = DashboardService.get_dashboard_data()
        except Exception as exc:
            tb.dialogs.Messagebox.show_error(f"Impossible de charger les notifications.\n\n{exc}", "Notifications")
            return

        self._notification_data = data
        count = int(data.get("retard", 0) or 0) + int(data.get("echeance", 0) or 0)
        self.set_notification_count(count)

        win = tk.Toplevel(self.winfo_toplevel())
        self._notification_window = win
        win.title("Centre de notifications")
        win.geometry("560x560")
        win.minsize(500, 420)
        win.configure(bg="#eef2f6")
        win.transient(self.winfo_toplevel())

        def close_window():
            if win.winfo_exists():
                win.destroy()
            self._notification_window = None

        win.protocol("WM_DELETE_WINDOW", close_window)

        header = tb.Frame(win, bootstyle="light", padding=(18, 14))
        header.pack(fill="x")
        tb.Label(header, text="🔔  Centre de notifications", font=("Segoe UI", 18, "bold"), bootstyle="dark").pack(side="left")
        tb.Button(header, text="↻ Actualiser", bootstyle="secondary-outline", command=lambda: self._reload_notification_window(win), padding=(10, 7)).pack(side="right")

        body = tb.Frame(win, bootstyle="light", padding=(18, 4, 18, 12))
        body.pack(fill="both", expand=True)
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        self._notification_summary = tb.Frame(body, bootstyle="light")
        self._notification_summary.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._notification_list_frame = tb.Frame(body, bootstyle="light")
        self._notification_list_frame.grid(row=1, column=0, sticky="nsew")

        footer = tb.Frame(win, bootstyle="light", padding=(18, 10))
        footer.pack(fill="x")
        tb.Button(footer, text="Fermer", bootstyle="secondary", command=close_window, padding=(12, 8)).pack(side="right")

        self._populate_notification_window(data)
        win.update_idletasks()
        parent = self.winfo_toplevel()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - win.winfo_width()) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - win.winfo_height()) // 2)
        win.geometry(f"{win.winfo_width()}x{win.winfo_height()}+{x}+{y}")

    def _reload_notification_window(self, win):
        if not win.winfo_exists():
            return
        try:
            data = DashboardService.get_dashboard_data()
        except Exception as exc:
            tb.dialogs.Messagebox.show_error(f"Impossible de charger les notifications.\n\n{exc}", "Notifications")
            return
        self._notification_data = data
        count = int(data.get("retard", 0) or 0) + int(data.get("echeance", 0) or 0)
        self.set_notification_count(count)
        self._populate_notification_window(data)

    def _populate_notification_window(self, data):
        for widget in self._notification_summary.winfo_children():
            widget.destroy()
        for widget in self._notification_list_frame.winfo_children():
            widget.destroy()

        retard = int(data.get("retard", 0) or 0)
        echeance = int(data.get("echeance", 0) or 0)
        self._notification_summary.columnconfigure(0, weight=1)
        self._notification_summary.columnconfigure(1, weight=1)
        tb.Label(self._notification_summary, text=f"Retards : {retard}", font=("Segoe UI", 12, "bold"), bootstyle="danger").grid(row=0, column=0, sticky="w", padx=4)
        tb.Label(self._notification_summary, text=f"Échéances : {echeance}", font=("Segoe UI", 12, "bold"), bootstyle="warning").grid(row=0, column=1, sticky="w", padx=4)

        items = []
        for f in data.get("factures_retard", [])[:50]:
            items.append(("RETARD", f))
        for f in data.get("factures_echeance", [])[:50]:
            items.append(("ÉCHÉANCE", f))

        if not items:
            tb.Label(self._notification_list_frame, text="Aucune notification.", font=("Segoe UI", 12), bootstyle="success").pack(anchor="w", pady=12)
            return

        for kind, item in items:
            text = str(item)
            tb.Label(self._notification_list_frame, text=f"• {kind} — {text}", font=("Segoe UI", 11), wraplength=500, justify="left", anchor="w").pack(fill="x", pady=5)
