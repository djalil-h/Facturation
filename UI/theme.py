import ttkbootstrap as tb
from tkinter import ttk


# Palette pensée pour une lecture confortable sur écran et pour les utilisateurs âgés.
# Contraste élevé, couleurs sobres et aucune dépendance à un vert dominant.
BG = "#eef2f6"
SURFACE = "#ffffff"
SURFACE_ALT = "#e7edf3"
TEXT = "#172033"
MUTED = "#4b5b6b"
PRIMARY = "#1f4e79"
PRIMARY_DARK = "#163a5c"
ACCENT = "#2f75b5"
BORDER = "#aebdca"
DANGER = "#b42318"
WARNING = "#a15c00"
SUCCESS = "#166534"

FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 11, "bold")
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_LARGE = (FONT_FAMILY, 24, "bold")


def apply_theme(window):
    """Applique un thème accessible : grands caractères, contraste fort et boutons lisibles."""
    window.configure(bg=BG)
    style = ttk.Style(window)

    style.configure("TLabel", font=FONT_NORMAL, foreground=TEXT, background=BG)
    style.configure("TFrame", background=BG)
    style.configure(
        "TLabelframe",
        background=SURFACE,
        bordercolor=BORDER,
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=SURFACE,
        foreground=TEXT,
        font=FONT_BOLD,
    )

    style.configure(
        "Modern.Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT,
        rowheight=44,
        font=(FONT_FAMILY, 11),
        borderwidth=1,
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=SURFACE_ALT,
        foreground=TEXT,
        font=(FONT_FAMILY, 11, "bold"),
        relief="flat",
        padding=(10, 10),
    )
    style.map(
        "Modern.Treeview",
        background=[("selected", PRIMARY)],
        foreground=[("selected", "white")],
    )

    style.configure("TEntry", padding=10, font=FONT_NORMAL)
    style.configure("TCombobox", padding=9, font=FONT_NORMAL)
    style.configure("TButton", font=FONT_BOLD, padding=(12, 9))

    # Styles utilisés par certains widgets ttkbootstrap/ttk.
    style.configure("Accessible.TButton", font=FONT_BOLD, padding=(14, 10))
    style.configure("Accessible.TEntry", font=FONT_NORMAL, padding=10)

    return style
