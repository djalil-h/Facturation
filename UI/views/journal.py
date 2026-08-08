import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from database.db import get_session
from database.models import JournalAction

class JournalView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Journal Administrateur")
        self._build()
        self.refresh()

    def _build(self):
        tb.Label(self.body, text="Journal des actions administrateur", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 15))
        bar = tb.Frame(self.body)
        bar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        tb.Entry(bar, textvariable=self.search_var, width=45).pack(side="left", ipady=5)
        tb.Label(bar, text="  Action / utilisateur / description").pack(side="left")
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(bar, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh).pack(side="right")
        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "Action", "Description", "Utilisateur", "Date"))
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        session = get_session()
        try:
            records = session.query(JournalAction).order_by(JournalAction.date_action.desc()).all()
            search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
            rows = []
            for item in records:
                values = [str(item.id), item.action or "", item.description or "", item.utilisateur or "", str(item.date_action)]
                if search and not any(search in value.lower() for value in values):
                    continue
                rows.append(tuple(values))
            self.table.load_data(rows)
            self.table.autosize()
        except Exception as exc:
            messagebox.showerror("Journal", f"Impossible de charger le journal.\n\n{exc}")
        finally:
            session.close()
