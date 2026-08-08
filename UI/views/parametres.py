import os
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as tb

from UI.base_view import BaseView
from config import APP_NAME, PHARMACY_NAME, APP_VERSION, BACKUP_DIR, DATABASE_FILE
from database.db import engine
from services.backup_service import create_backup, list_backups, restore_backup


class ParametresView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Paramètres")
        self._build()
        self.refresh_backups()

    def _build(self):
        tb.Label(
            self.body,
            text="Configuration et maintenance",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(0, 15))

        info = tb.LabelFrame(self.body, text="Application", padding=15)
        info.pack(fill="x", pady=(0, 15))
        tb.Label(info, text=f"Nom : {APP_NAME}").pack(anchor="w")
        tb.Label(info, text=f"Établissement : {PHARMACY_NAME}").pack(anchor="w", pady=3)
        tb.Label(info, text=f"Version : {APP_VERSION}").pack(anchor="w")
        tb.Label(info, text=f"Base de données : {DATABASE_FILE}", wraplength=1000).pack(anchor="w", pady=(3, 0))

        backup = tb.LabelFrame(self.body, text="Sauvegarde de la base de données", padding=15)
        backup.pack(fill="both", expand=True, pady=(0, 15))

        actions = tb.Frame(backup)
        actions.pack(fill="x", pady=(0, 10))
        tb.Button(actions, text="💾 Créer une sauvegarde", bootstyle="success", command=self.create_backup).pack(side="left", padx=(0, 8))
        tb.Button(actions, text="📁 Ouvrir le dossier", bootstyle="secondary-outline", command=self.open_backup_folder).pack(side="left")
        tb.Button(actions, text="↻ Actualiser", bootstyle="secondary-outline", command=self.refresh_backups).pack(side="right")

        self.listbox = tk.Listbox(backup, height=8)
        self.listbox.pack(fill="both", expand=True, pady=(5, 8))
        self.backups = []

        bottom = tb.Frame(backup)
        bottom.pack(fill="x")
        tb.Button(bottom, text="Restaurer la sauvegarde sélectionnée", bootstyle="warning", command=self.restore_selected).pack(side="left")
        tb.Label(bottom, text="Une restauration nécessite de relancer l'application.").pack(side="left", padx=12)

    def create_backup(self):
        try:
            path = create_backup()
            self.refresh_backups()
            messagebox.showinfo("Sauvegarde", f"Sauvegarde créée avec succès :\n\n{path}", parent=self)
        except Exception as exc:
            messagebox.showerror("Sauvegarde", f"Impossible de créer la sauvegarde.\n\n{exc}", parent=self)

    def open_backup_folder(self):
        try:
            os.startfile(str(BACKUP_DIR))
        except Exception as exc:
            messagebox.showerror("Sauvegarde", f"Impossible d'ouvrir le dossier.\n\n{exc}", parent=self)

    def refresh_backups(self):
        if not hasattr(self, "listbox"):
            return
        self.backups = list_backups()
        self.listbox.delete(0, tk.END)
        for path in self.backups:
            self.listbox.insert(tk.END, path.name)

    def restore_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Restauration", "Sélectionnez d'abord une sauvegarde.", parent=self)
            return

        path = self.backups[selection[0]]
        confirm = messagebox.askyesno(
            "Restauration",
            "La base de données actuelle sera remplacée par cette sauvegarde.\n\n"
            f"{path.name}\n\nContinuer ?",
            parent=self,
        )
        if not confirm:
            return

        try:
            # Ferme les connexions SQLAlchemy avant de remplacer le fichier SQLite.
            engine.dispose()
            restore_backup(path)
            messagebox.showinfo(
                "Restauration terminée",
                "La base a été restaurée. Fermez puis relancez l'application pour charger les données restaurées.",
                parent=self,
            )
        except Exception as exc:
            messagebox.showerror("Restauration", f"Impossible de restaurer la sauvegarde.\n\n{exc}", parent=self)
