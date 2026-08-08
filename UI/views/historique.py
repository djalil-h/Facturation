import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from database.db import get_session
from database.models import Historique

class HistoriqueView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Historique")
        self._build()
        self.refresh()

    def _build(self):
        tb.Label(self.body, text="Historique des opérations", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 15))
        bar = tb.Frame(self.body)
        bar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        tb.Entry(bar, textvariable=self.search_var, width=45).pack(side="left", ipady=5)
        tb.Label(bar, text="  Facture / action / utilisateur").pack(side="left")
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(bar, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh).pack(side="right")
        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "Facture", "Action", "Détails", "Utilisateur", "Date"))
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        session = get_session()
        try:
            records = session.query(Historique).order_by(Historique.date_action.desc()).all()
            search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
            rows = []
            for item in records:
                numero = item.facture.numero if item.facture else ""
                values = [str(item.id), numero, item.action or "", item.details or "", item.utilisateur or "", str(item.date_action)]
                if search and not any(search in value.lower() for value in values):
                    continue
                rows.append(tuple(values))
            self.table.load_data(rows)
            self.table.autosize()
        except Exception as exc:
            messagebox.showerror("Historique", f"Impossible de charger l'historique.\n\n{exc}")
        finally:
            session.close()
