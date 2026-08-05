from database import create_database
from services.user_service import create_admin

from UI.app import FacturationApp

create_database()

create_admin()

app = FacturationApp()

app.mainloop()