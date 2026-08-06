import tkinter as tk
from tkinter import ttk


class ModernTable(ttk.Frame):

    def __init__(self, master, columns):

        super().__init__(master)

        self.columns = columns

        self._sort_reverse = {}

        style = ttk.Style()

        style.configure(
            "Modern.Treeview",
            rowheight=34,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Modern.Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Modern.Treeview",
            background=[("selected", "#0A64A4")],
            foreground=[("selected", "white")]
        )

        self.tree = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            style="Modern.Treeview"
        )

        self.v_scroll = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )

        self.h_scroll = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for col in self.columns:

            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort(c)
            )

            self.tree.column(
                col,
                anchor="center",
                width=140,
                minwidth=80
            )

        self.tree.tag_configure("odd", background="#F8F9FA")
        self.tree.tag_configure("even", background="white")

        self.tree.tag_configure("payee", foreground="#198754")
        self.tree.tag_configure("impayee", foreground="#DC3545")
        self.tree.tag_configure("retard", foreground="#FF8800")

    # ------------------------------

    def clear(self):

        self.tree.delete(*self.tree.get_children())

    # ------------------------------

    def load_data(self, rows):

        self.clear()

        for index, row in enumerate(rows):

            tags = []

            if index % 2 == 0:
                tags.append("even")
            else:
                tags.append("odd")

            text = " ".join(str(x).lower() for x in row)

            if "payé" in text:
                tags.append("payee")

            elif "impayé" in text:
                tags.append("impayee")

            elif "retard" in text:
                tags.append("retard")

            self.tree.insert(
                "",
                tk.END,
                values=row,
                tags=tuple(tags)
            )

    # ------------------------------

    def get_selected(self):

        selection = self.tree.selection()

        if not selection:
            return None

        return self.tree.item(selection[0])["values"]

    # ------------------------------

    def delete_selected(self):

        selection = self.tree.selection()

        if selection:

            self.tree.delete(selection[0])

    # ------------------------------

    def bind_double_click(self, callback):

        self.tree.bind("<Double-1>", callback)

    # ------------------------------

    def bind_right_click(self, callback):

        self.tree.bind("<Button-3>", callback)

    # ------------------------------

    def sort(self, column):

        data = []

        for child in self.tree.get_children():

            data.append(
                (
                    self.tree.set(child, column),
                    child
                )
            )

        reverse = self._sort_reverse.get(column, False)

        try:

            data.sort(
                key=lambda x: float(str(x[0]).replace(",", ".")),
                reverse=reverse
            )

        except:

            data.sort(
                key=lambda x: str(x[0]).lower(),
                reverse=reverse
            )

        for index, (_, child) in enumerate(data):

            self.tree.move(child, "", index)

        self._sort_reverse[column] = not reverse

    # ------------------------------

    def refresh(self, rows):

        self.load_data(rows)

    # ------------------------------

    def autosize(self):

        for col in self.columns:

            width = max(
                len(col) * 10,
                120
            )

            for item in self.tree.get_children():

                value = str(self.tree.set(item, col))

                width = max(width, len(value) * 8)

            self.tree.column(col, width=width)