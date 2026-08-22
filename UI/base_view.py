import ttkbootstrap as tb
from ttkbootstrap.constants import *


_original_toplevel = tb.Toplevel


class CenteredToplevel(_original_toplevel):
    """Toplevel centré automatiquement et adapté à la hauteur de l'écran."""

    def geometry(self, geometry_string=None):
        if geometry_string and "x" in geometry_string and "+" not in geometry_string:
            try:
                requested_w, requested_h = (int(v) for v in geometry_string.split("x", 1))
                screen_w = self.winfo_screenwidth()
                screen_h = self.winfo_screenheight()

                width = min(requested_w, max(400, screen_w - 40))
                height = min(requested_h, max(400, screen_h - 80))

                result = super().geometry(f"{width}x{height}")
                self.update_idletasks()
                x = max(0, (screen_w - width) // 2)
                y = max(0, (screen_h - height) // 2)
                return super().geometry(f"{width}x{height}+{x}+{y}")
            except (TypeError, ValueError):
                pass
        return super().geometry(geometry_string)


# Tous les dialogues de l'application utilisent automatiquement ce comportement.
tb.Toplevel = CenteredToplevel


class BaseView(tb.Frame):
    """Socle visuel commun à toutes les pages, avec une typographie accessible."""

    def __init__(self, master, title):
        super().__init__(master, bootstyle="light", padding=(6, 6, 6, 0))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tb.Frame(self, bootstyle="light", padding=(10, 10, 10, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tb.Label(
            header,
            text=title,
            font=("Segoe UI", 21, "bold"),
            bootstyle="dark",
        ).grid(row=0, column=0, sticky="w")

        self.body = tb.Frame(self, bootstyle="light")
        self.body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)
