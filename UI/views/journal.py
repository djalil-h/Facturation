import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.base_view import BaseView


class JournalView(BaseView):

    def __init__(self, master):

        super().__init__(master, "Journal Administrateur")

        tb.Label(
            self.body,
            text="Journal des actions (Admin uniquement)",
            font=("Segoe UI", 12)
        ).pack(anchor="w")