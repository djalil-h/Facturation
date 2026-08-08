import ttkbootstrap as tb


class SearchBar(tb.Frame):
    """Barre de recherche commune, compacte et responsive."""

    def __init__(self, master, command=None):
        super().__init__(master, bootstyle="light", padding=(0, 2))
        self.command = command
        self.columnconfigure(0, weight=1)

        self.entry = tb.Entry(self, font=("Segoe UI", 10))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=5)
        self.entry.bind("<KeyRelease>", self.search)

        tb.Button(
            self, text="🔎 Rechercher", bootstyle="primary", command=self.search,
            padding=(10, 6)
        ).grid(row=0, column=1)

    def search(self, _event=None):
        if self.command:
            self.command(self.entry.get())
