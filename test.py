from database import create_database
from services.user_service import create_admin, login

create_database()
create_admin()

user = login("admin", "admin123")

print(user.username)
print(user.role)