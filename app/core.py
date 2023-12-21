from fastapi.templating import Jinja2Templates
import fastapi_users

current_user_optional = fastapi_users.current_user(optional=True)
current_user_admin = fastapi_users.current_user(active=True, superuser=True)
templates = Jinja2Templates(directory="templates")