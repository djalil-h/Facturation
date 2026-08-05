import ttkbootstrap as tb
from ttkbootstrap.constants import *

from UI.sidebar import Sidebar
from UI.dashboard import Dashboard


class FacturationApp(tb.Window):

    def __init__(self):

        super().__init__(themename="flatly")

        self.title("Facturation - Pharmacie Hamzaoui Hamid")

        self.geometry("1500x850")

        self.minsize(1300, 750)

        self.create_layout()

    def create_layout(self):

        self.sidebar = Sidebar(self)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = tb.Frame(self)
        self.content.pack(side=LEFT, fill=BOTH, expand=True)

        self.show_dashboard()

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):

        self.clear_content()

        Dashboard(self.content).pack(fill=BOTH, expand=True)