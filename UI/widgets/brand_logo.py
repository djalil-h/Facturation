import tkinter as tk
import ttkbootstrap as tb


class BrandLogo(tb.Frame):
    """Logo Hamzaoui Facturation dessiné en Tkinter, sans dépendance image."""

    def __init__(self, master, width=250, height=150, dark=False, compact=False):
        super().__init__(master, bootstyle="dark" if dark else "light")
        self.width = width
        self.height = height
        self.dark = dark
        self.compact = compact
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg="#263238" if dark else "#f4fbf8",
        )
        self.canvas.pack(fill="both", expand=True)
        self._draw()

    def _draw(self):
        c = self.canvas
        bg = "#263238" if self.dark else "#f4fbf8"
        green = "#22c55e"
        teal = "#0f766e"
        text = "#ffffff" if self.dark else "#164e63"
        muted = "#cbd5e1" if self.dark else "#475569"

        c.configure(bg=bg)
        cx = self.width / 2
        scale = min(self.width / 250, self.height / 150)

        # HH monogram.
        c.create_text(cx, 37 * scale, text="HH", font=("Segoe UI", max(28, int(55 * scale)), "bold"), fill=teal)

        # Bâton d'Asclépios stylisé au centre.
        x = cx
        top = 8 * scale
        bottom = 70 * scale
        c.create_line(x, top, x, bottom, fill=green, width=max(2, int(3 * scale)))
        c.create_oval(x - 5 * scale, top - 6 * scale, x + 5 * scale, top + 4 * scale, fill=green, outline=green)
        c.create_arc(x - 35 * scale, 20 * scale, x + 8 * scale, 62 * scale, start=285, extent=180, style="arc", outline=green, width=max(2, int(3 * scale)))
        c.create_arc(x - 8 * scale, 35 * scale, x + 35 * scale, 77 * scale, start=105, extent=180, style="arc", outline=green, width=max(2, int(3 * scale)))
        c.create_arc(x - 48 * scale, 2 * scale, x - 5 * scale, 28 * scale, start=20, extent=85, style="arc", outline=green, width=max(2, int(2 * scale)))
        c.create_arc(x + 5 * scale, 2 * scale, x + 48 * scale, 28 * scale, start=75, extent=85, style="arc", outline=green, width=max(2, int(2 * scale)))

        if self.compact:
            c.create_text(cx, 91 * scale, text="Hamzaoui", font=("Segoe UI", max(12, int(20 * scale)), "bold"), fill=text)
            c.create_text(cx, 114 * scale, text="FACTURATION", font=("Segoe UI", max(8, int(10 * scale)), "bold"), fill=muted)
        else:
            c.create_text(cx, 94 * scale, text="Hamzaoui", font=("Segoe UI", max(16, int(27 * scale)), "bold"), fill=text)
            c.create_line(cx - 65 * scale, 108 * scale, cx + 65 * scale, 108 * scale, fill=green, width=max(1, int(2 * scale)))
            c.create_text(cx, 126 * scale, text="FACTURATION", font=("Segoe UI", max(9, int(13 * scale)), "bold"), fill=muted)
