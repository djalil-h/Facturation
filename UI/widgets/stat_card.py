import ttkbootstrap as tb


class StatCard(tb.Frame):
    """Carte KPI compacte et homogène."""

    def __init__(self, master, title, value, icon="📊", color="primary"):
        super().__init__(master, bootstyle="light", padding=(12, 10))
        self.columnconfigure(1, weight=1)

        accent = tb.Frame(self, width=4, bootstyle=color)
        accent.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 10))

        tb.Label(self, text=icon, font=("Segoe UI Emoji", 22), bootstyle="secondary").grid(
            row=0, column=1, rowspan=2, padx=(0, 10)
        )
        tb.Label(
            self, text=title, font=("Segoe UI", 9), bootstyle="secondary"
        ).grid(row=0, column=2, sticky="w")
        self.lbl_value = tb.Label(
            self, text=value, font=("Segoe UI", 18, "bold"), bootstyle=color
        )
        self.lbl_value.grid(row=1, column=2, sticky="w")

    def set_value(self, value):
        self.lbl_value.configure(text=value)
