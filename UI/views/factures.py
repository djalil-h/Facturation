import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import date, datetime
import ttkbootstrap as tb

from UI.base_view import BaseView
from UI.widgets.modern_table import ModernTable
from services.facture_service import ajouter_facture, liste_factures, modifier_facture, supprimer_facture, ajouter_paiement, liste_paiements, rechercher_factures
from services.fournisseur_service import liste_fournisseurs
from services.import_service import analyser_factures_excel, importer_factures_excel
from services.export_service import exporter_factures_excel, creer_modele_factures_excel


class FacturesView(BaseView):
    def __init__(self, master):
        super().__init__(master, "Gestion des factures")
        self.factures = []
        self.fournisseurs = []
        self._build()
        self.refresh()

    def _current_user(self):
        return self.winfo_toplevel().get_current_user()

    @staticmethod
    def _format_date(value):
        if not value:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        try:
            return date.fromisoformat(str(value)[:10]).strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def _format_amount(value):
        try:
            return f"{float(value or 0):,.2f} DA".replace(",", " ")
        except (TypeError, ValueError):
            return "0,00 DA"

    def _build(self):
        header = tb.Frame(self.body)
        header.pack(fill="x", pady=(0, 12))
        title_box = tb.Frame(header)
        title_box.pack(side="left", fill="x", expand=True)
        tb.Label(title_box, text="Factures & avoirs", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(title_box, text="Consultez, importez et gérez les pièces fournisseurs", bootstyle="secondary").pack(anchor="w", pady=(1, 0))

        actions = tb.Frame(header)
        actions.pack(side="right")
        for text, style, command in [
            ("⬇  Exporter", "success-outline", self.export_excel),
            ("📄  Modèle", "secondary-outline", self.export_template),
            ("⬆  Importer", "info-outline", self.import_excel),
            ("＋  Nouvelle pièce", "success", self.open_add_dialog),
        ]:
            tb.Button(actions, text=text, bootstyle=style, command=command, padding=(10, 7)).pack(side="left", padx=3)

        toolbar = tb.Frame(self.body, padding=(10, 9))
        toolbar.pack(fill="x", pady=(0, 10))
        toolbar.columnconfigure(0, weight=1)
        search_box = tb.Frame(toolbar)
        search_box.grid(row=0, column=0, sticky="ew")
        self.search_var = tk.StringVar()
        tb.Label(search_box, text="🔎", font=("Segoe UI", 11)).pack(side="left", padx=(0, 5))
        tb.Entry(search_box, textvariable=self.search_var).pack(side="left", fill="x", expand=True, ipady=4)
        tb.Label(search_box, text="  Numéro / fournisseur", bootstyle="secondary").pack(side="left", padx=8)
        self.status_var = tk.StringVar(value="Tous les statuts")
        self.status_combo = tb.Combobox(toolbar, textvariable=self.status_var, state="readonly", width=22, values=["Tous les statuts", "Impayée", "Partiellement payée", "Payée"])
        self.status_combo.grid(row=0, column=1, padx=10)
        self.status_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.search_var.trace_add("write", lambda *_: self.refresh())
        tb.Button(toolbar, text="↻  Actualiser", bootstyle="secondary-outline", command=self.refresh, padding=(10, 6)).grid(row=0, column=2)

        frame = tb.Frame(self.body)
        frame.pack(fill="both", expand=True)
        self.table = ModernTable(frame, ("ID", "Type", "N°", "Fournisseur", "Date", "Échéance", "Montant", "Payé", "Reste", "Statut"))
        self.table.pack(fill="both", expand=True)
        self.table.bind_double_click(self._edit_selected)

        footer = tb.Frame(self.body, padding=(0, 10, 0, 0))
        footer.pack(fill="x")
        self.count_label = tb.Label(footer, text="0 pièce", font=("Segoe UI", 9, "bold"), bootstyle="secondary")
        self.count_label.pack(side="left")
        buttons = tb.Frame(footer)
        buttons.pack(side="right")
        for text, style, command in [
            ("✎  Modifier", "primary-outline", self._edit_selected),
            ("💰  Paiement", "success", self.open_payment_dialog),
            ("✕  Supprimer", "danger-outline", self._delete_selected),
        ]:
            tb.Button(buttons, text=text, bootstyle=style, command=command, padding=(10, 7)).pack(side="left", padx=3)

    def refresh(self):
        try:
            self.fournisseurs = liste_fournisseurs()
            status = self.status_var.get() if hasattr(self, "status_var") else "Tous les statuts"
            enum_status = None if status == "Tous les statuts" else status
            search = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
            self.factures = rechercher_factures(statut=enum_status)
            if search:
                self.factures = [f for f in self.factures if search in str(f.numero).lower() or search in str(getattr(f.fournisseur, "nom", "")).lower()]
        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de charger les pièces.\n\n{exc}")
            return
        rows = []
        for f in self.factures:
            type_piece = getattr(f, "type_piece", "Facture")
            montant = float(f.montant or 0)
            fournisseur_nom = getattr(f.fournisseur, "nom", "") if f.fournisseur else ""
            rows.append((
                f.id, type_piece, f.numero, fournisseur_nom,
                self._format_date(f.date_facture), self._format_date(f.date_echeance),
                self._format_amount(montant), self._format_amount(f.montant_paye),
                self._format_amount(f.reste), getattr(f.statut, "value", f.statut)
            ))
        self.table.load_data(rows)
        self.table.autosize()
        self.count_label.configure(text=f"{len(rows)} pièce{'s' if len(rows) != 1 else ''}")

    def export_excel(self):
        path = filedialog.asksaveasfilename(title="Exporter les factures", defaultextension=".xlsx", filetypes=[("Fichier Excel", "*.xlsx")], initialfile="factures_export.xlsx")
        if not path:
            return
        try:
            exporter_factures_excel(path)
            messagebox.showinfo("Export Excel", f"Export terminé.\n\nFichier : {path}")
        except Exception as exc:
            messagebox.showerror("Export Excel", f"Impossible d'exporter les factures.\n\n{exc}")

    def export_template(self):
        path = filedialog.asksaveasfilename(title="Créer le modèle Excel", defaultextension=".xlsx", filetypes=[("Fichier Excel", "*.xlsx")], initialfile="modele_import_factures.xlsx")
        if not path:
            return
        try:
            creer_modele_factures_excel(path)
            messagebox.showinfo("Modèle Excel", f"Modèle créé.\n\nTu peux le remplir puis utiliser « Importer Excel ».\n\nFichier : {path}")
        except Exception as exc:
            messagebox.showerror("Modèle Excel", f"Impossible de créer le modèle.\n\n{exc}")

    def import_excel(self):
        path = filedialog.askopenfilename(title="Choisir le fichier Excel", filetypes=[("Fichiers Excel", "*.xlsx")])
        if not path:
            return
        try:
            preview = analyser_factures_excel(path)
        except Exception as exc:
            messagebox.showerror("Analyse Excel", f"Impossible d'analyser le fichier.\n\n{exc}")
            return

        preview_window = tb.Toplevel(self)
        preview_window.title(f"Aperçu avant import — {preview['filename']}")
        preview_window.geometry("1080x700")
        preview_window.minsize(900, 600)
        preview_window.transient(self.winfo_toplevel())
        preview_window.grab_set()

        outer = tb.Frame(preview_window, padding=18)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(4, weight=1)

        tb.Label(outer, text="Aperçu avant import", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        tb.Label(outer, text=preview["filename"], bootstyle="secondary").grid(row=1, column=0, sticky="w", pady=(0, 12))

        summary = tb.Frame(outer)
        summary.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        for i in range(4):
            summary.columnconfigure(i, weight=1)
        cards = [
            ("À importer", preview["to_import"], "success"),
            ("Factures", preview["factures"], "primary"),
            ("Avoirs", preview["avoirs"], "warning"),
            ("Doublons", preview["duplicates"], "secondary"),
        ]
        for i, (title, value, style) in enumerate(cards):
            card = tb.Frame(summary, padding=(12, 8), bootstyle=style)
            card.grid(row=0, column=i, sticky="ew", padx=3)
            tb.Label(card, text=str(value), font=("Segoe UI", 18, "bold"), bootstyle=f"{style}-inverse").pack()
            tb.Label(card, text=title, font=("Segoe UI", 8), bootstyle=f"{style}-inverse").pack()

        net = preview["total_factures"] - preview["total_avoirs"]
        tb.Label(outer, text=f"Total factures : {self._format_amount(preview['total_factures'])}    •    Total avoirs : {self._format_amount(preview['total_avoirs'])}    •    Dette nette importée : {self._format_amount(net)}", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 4))
        suppliers = ", ".join(preview["suppliers"][:12])
        if len(preview["suppliers"]) > 12:
            suppliers += f" … (+{len(preview['suppliers']) - 12})"
        tb.Label(outer, text=f"Fournisseurs détectés : {suppliers or 'aucun'}", bootstyle="secondary").grid(row=3, column=0, sticky="e", pady=(0, 4))

        details = tb.Frame(outer)
        details.grid(row=4, column=0, sticky="nsew", pady=(8, 0))
        details.columnconfigure(0, weight=1)
        details.rowconfigure(0, weight=1)

        columns = ("status", "type", "numero", "date", "fournisseur", "montant", "origine")
        tree = tb.Treeview(details, columns=columns, show="headings", selectmode="browse")
        headings = {
            "status": "État", "type": "Type", "numero": "N° pièce", "date": "Date facture",
            "fournisseur": "Fournisseur", "montant": "Montant", "origine": "Origine"
        }
        widths = {"status": 95, "type": 85, "numero": 135, "date": 105, "fournisseur": 190, "montant": 130, "origine": 170}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center" if col not in ("fournisseur", "origine") else "w", stretch=col in ("fournisseur", "origine"))
        scroll = tb.Scrollbar(details, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        tree.tag_configure("avoir", foreground="#b36b00")
        tree.tag_configure("doublon", foreground="#777777")
        tree.tag_configure("anomalie", foreground="#c0392b")

        for row in preview["rows"][:1000]:
            sign = "AVOIR" if row["type_piece"] == "Avoir" else "FACTURE"
            status = row["status"]
            tag = "avoir" if sign == "AVOIR" else ""
            if "Doublon" in status:
                tag = "doublon"
            tree.insert("", "end", values=(
                status,
                sign,
                row["numero"],
                self._format_date(row.get("date_facture")),
                row["fournisseur"],
                self._format_amount(row["montant"]),
                f"{row['sheet']}:{row['excel_row']}"
            ), tags=(tag,) if tag else ())

        if len(preview["rows"]) > 1000:
            tree.insert("", "end", values=("INFO", "—", "—", "—", "—", "—", f"+{len(preview['rows']) - 1000} lignes"), tags=("doublon",))

        if preview["errors"]:
            anomaly_box = tb.Labelframe(outer, text="  ⚠ Anomalies à vérifier  ", padding=8)
            anomaly_box.grid(row=5, column=0, sticky="ew", pady=(8, 0))
            anomaly_text = "\n".join(f"• {error}" for error in preview["errors"][:10])
            if len(preview["errors"]) > 10:
                anomaly_text += f"\n• … et {len(preview['errors']) - 10} autre(s)."
            tb.Label(anomaly_box, text=anomaly_text, bootstyle="danger", justify="left", anchor="w").pack(fill="x")

        buttons = tb.Frame(outer)
        buttons.grid(row=6, column=0, sticky="ew", pady=(12, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=preview_window.destroy, padding=(12, 7)).pack(side="right", padx=4)

        def confirm_import():
            if preview["to_import"] == 0:
                messagebox.showwarning("Import", "Aucune nouvelle pièce à importer.", parent=preview_window)
                return
            if not messagebox.askyesno("Confirmer l'import", f"Importer {preview['to_import']} pièce(s) dans la base officielle ?\n\nLes doublons seront ignorés et les fournisseurs absents seront créés.", parent=preview_window):
                return
            try:
                result = importer_factures_excel(path, self._current_user(), creer_fournisseurs=True)
            except Exception as exc:
                messagebox.showerror("Import Excel", f"Import impossible.\n\n{exc}", parent=preview_window)
                return
            preview_window.destroy()
            self.refresh()
            message = f"Import terminé.\n\nPièces importées : {result['imported']}\nFactures : {result['factures']}\nAvoirs : {result['avoirs']}\nDoublons ignorés : {result['skipped']}\nFournisseurs créés : {result['suppliers_created']}"
            if result["payments_created"]:
                message += f"\nPaiements historiques : {result['payments_created']}"
            if result["errors"]:
                message += "\n\nAnomalies :\n" + "\n".join(result["errors"][:15])
            messagebox.showinfo("Import Excel", message)

        tb.Button(buttons, text=f"✓ Importer {preview['to_import']} pièce(s)", bootstyle="success", command=confirm_import, padding=(12, 7)).pack(side="right", padx=4)

    def _selected(self):
        values = self.table.get_selected()
        if not values:
            messagebox.showwarning("Sélection", "Sélectionnez une pièce.")
            return None
        try:
            selected_id = int(values[0])
        except (TypeError, ValueError):
            return None
        return next((f for f in self.factures if f.id == selected_id), None)

    def _edit_selected(self, _event=None):
        facture = self._selected()
        if facture:
            self.open_form_dialog(facture)

    def _delete_selected(self):
        facture = self._selected()
        if not facture:
            return
        libelle = getattr(facture, "type_piece", "Facture").lower()
        if not messagebox.askyesno("Confirmation", f"Supprimer {libelle} « {facture.numero} » ?"):
            return
        try:
            supprimer_facture(facture.id, self._current_user())
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erreur", f"Suppression impossible.\n\n{exc}")

    def _fournisseur_map(self):
        return {f.nom: f.id for f in self.fournisseurs}

    def open_add_dialog(self):
        self.open_form_dialog(None)

    def open_form_dialog(self, facture):
        dialog = tb.Toplevel(self)
        dialog.title("Modifier la pièce" if facture else "Nouvelle facture / avoir")
        dialog.geometry("600x720")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Modifier la pièce" if facture else "Nouvelle facture / avoir", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 18))
        tb.Label(box, text="Type de pièce *").pack(anchor="w", pady=(0, 3))
        type_var = tk.StringVar(value=getattr(facture, "type_piece", "Facture") if facture else "Facture")
        tb.Combobox(box, textvariable=type_var, state="readonly", values=["Facture", "Avoir"]).pack(fill="x", pady=(0, 8))
        entries = {}
        for label, key, value in [
            ("Numéro *", "numero", getattr(facture, "numero", "")),
            ("Date (AAAA-MM-JJ) *", "date_facture", getattr(facture, "date_facture", date.today())),
            ("Date échéance (AAAA-MM-JJ) *", "date_echeance", getattr(facture, "date_echeance", date.today())),
            ("Montant *", "montant", abs(getattr(facture, "montant", 0)) if facture else ""),
            ("Commentaire", "commentaire", getattr(facture, "commentaire", "") or "")
        ]:
            tb.Label(box, text=label).pack(anchor="w", pady=(7, 3))
            e = tb.Entry(box)
            e.insert(0, str(value))
            e.pack(fill="x")
            entries[key] = e
        tb.Label(box, text="Fournisseur *").pack(anchor="w", pady=(7, 3))
        names = list(self._fournisseur_map().keys())
        fournisseur_var = tk.StringVar()
        combo = tb.Combobox(box, textvariable=fournisseur_var, state="readonly", values=names)
        combo.pack(fill="x")
        if facture and facture.fournisseur:
            fournisseur_var.set(facture.fournisseur.nom)
        elif names:
            combo.current(0)
        hint = tb.Label(box, text="", bootstyle="info")
        hint.pack(anchor="w", pady=(12, 0))

        def update_hint(*_):
            hint.configure(text="Avoir : le montant sera déduit de la dette fournisseur et ne pourra pas recevoir de paiement." if type_var.get() == "Avoir" else "Facture : le montant augmente la dette fournisseur et peut recevoir des paiements.")
        type_var.trace_add("write", update_hint)
        update_hint()
        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=(25, 0))
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)

        def save():
            numero = entries["numero"].get().strip()
            if not numero or not fournisseur_var.get():
                messagebox.showwarning("Validation", "Numéro et fournisseur sont obligatoires.", parent=dialog)
                return
            try:
                d_facture = datetime.strptime(entries["date_facture"].get().strip(), "%Y-%m-%d").date()
                d_echeance = datetime.strptime(entries["date_echeance"].get().strip(), "%Y-%m-%d").date()
                montant = float(entries["montant"].get().replace(",", "."))
                if montant <= 0:
                    raise ValueError("Le montant doit être strictement supérieur à zéro.")
                if d_echeance < d_facture:
                    raise ValueError("La date d'échéance ne peut pas être avant la date de facture.")
                fournisseur_id = self._fournisseur_map()[fournisseur_var.get()]
                if facture:
                    modifier_facture(facture.id, fournisseur_id, numero, d_facture, d_echeance, montant, entries["commentaire"].get().strip(), self._current_user(), type_var.get())
                else:
                    ajouter_facture(numero, fournisseur_id, d_facture, d_echeance, montant, entries["commentaire"].get().strip(), self._current_user(), type_var.get())
            except Exception as exc:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer la pièce.\n\n{exc}", parent=dialog)
                return
            dialog.destroy()
            self.refresh()
        tb.Button(buttons, text="Enregistrer", bootstyle="success", command=save).pack(side="right")

    def open_payment_dialog(self):
        facture = self._selected()
        if not facture:
            return
        if getattr(facture, "type_piece", "Facture") == "Avoir":
            messagebox.showinfo("Paiement", "Un avoir diminue la dette fournisseur et ne peut pas recevoir de paiement.")
            return
        if facture.reste <= 0:
            messagebox.showinfo("Paiement", "Cette facture est déjà entièrement payée.")
            return
        dialog = tb.Toplevel(self)
        dialog.title(f"Paiement — {facture.numero}")
        dialog.geometry("500x430")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        box = tb.Frame(dialog, padding=25)
        box.pack(fill="both", expand=True)
        tb.Label(box, text="Enregistrer un paiement", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tb.Label(box, text=f"Facture : {facture.numero}\nReste à payer : {facture.reste:,.2f} DA", font=("Segoe UI", 11)).pack(anchor="w", pady=15)
        tb.Label(box, text="Montant *").pack(anchor="w", pady=(5, 3))
        amount = tb.Entry(box)
        amount.insert(0, str(facture.reste))
        amount.pack(fill="x")
        tb.Label(box, text="Mode de paiement").pack(anchor="w", pady=(10, 3))
        mode = tb.Combobox(box, state="readonly", values=["Espèces", "Chèque", "Virement", "Carte", "Autre"])
        mode.current(0)
        mode.pack(fill="x")
        tb.Label(box, text="Référence").pack(anchor="w", pady=(10, 3))
        reference = tb.Entry(box)
        reference.pack(fill="x")

        def save():
            try:
                ajouter_paiement(facture.id, float(amount.get().replace(",", ".")), mode.get(), reference.get().strip(), self._current_user())
            except Exception as exc:
                messagebox.showerror("Paiement refusé", str(exc), parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        buttons = tb.Frame(box)
        buttons.pack(fill="x", pady=25)
        tb.Button(buttons, text="Annuler", bootstyle="secondary-outline", command=dialog.destroy).pack(side="right", padx=5)
        tb.Button(buttons, text="Enregistrer le paiement", bootstyle="success", command=save).pack(side="right")

    def show_payments(self):
        facture = self._selected()
        if not facture:
            return
        paiements = liste_paiements(facture.id)
        if not paiements:
            messagebox.showinfo("Paiements", "Aucun paiement enregistré.")
            return
        details = "\n".join(f"{self._format_date(p.date_paiement)} — {self._format_amount(p.montant)} — {p.mode_paiement or '-'} — {p.reference or '-'}" for p in paiements)
        messagebox.showinfo(f"Paiements — {facture.numero}", details)
