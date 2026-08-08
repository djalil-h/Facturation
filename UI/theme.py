import ttkbootstrap as tb
from tkinter import ttk


BG = "#f5f7fa"
SURFACE = "#ffffff"
SURFACE_ALT = "#eef3f6"
TEXT = "#17212b"
MUTED = "#6b7785"
PRIMARY = "#0f766e"
PRIMARY_DARK = "#0b5d57"
ACCENT = "#22b38a"
BORDER = "#dbe3e8"
DANGER = "#dc4c4c"
WARNING = "#e59b22"
SUCCESS = "#1f9d72"


def apply_theme(window):
    """Applique le langage visuel Hamzaoui à toute l'application."""
    window.configure(bg=BG)
    style = ttk.Style(window)

    style.configure("TLabel", font=("Segoe UI", 10), foreground=TEXT)
    style.configure("TFrame", background=BG)
    style.configure("TLabelframe", background=SURFACE, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=SURFACE, foreground=TEXT, font=("Segoe UI", 10, "bold"))

    style.configure("Modern.Treeview", background=SURFACE, fieldbackground=SURFACE,
                    foreground=TEXT, rowheight=38, font=("Segoe UI", 9))
    style.configure("Modern.Treeview.Heading", background="#e8f0f2", foreground=TEXT,
                    font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 8))
    style.map("Modern.Treeview", background=[("selected", PRIMARY)],
              foreground=[("selected", "white")])

    style.configure("TEntry", padding=7)
    style.configure("TCombobox", padding=6)
    style.configure("TButton", font=("Segoe UI", 9, "bold"))

    return style
