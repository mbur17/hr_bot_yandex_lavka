from pathlib import Path

import nest_asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.admin.config import (
    CustomAdmin,
    NodeException,
    authentication_backend,
    node_exception_handler,
)
from src.app.admin.views import (
    ButtonAdmin,
    HRRequestAdmin,
    ImageAdmin,
    NodeAdmin,
    UserAdmin,
)
from src.app.api.routers import v1_router
from src.app.core.config import settings
from src.app.core.db import engine
from src.app.core.init_db import lifespan

nest_asyncio.apply()

app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.mount('/static', StaticFiles(directory='src/app/static'), name='static')
app.mount('/media', StaticFiles(directory='node_images'), name='media')

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

admin = CustomAdmin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    title='HR Bot Admin',
    logo_url='/static/logo.svg',
    favicon_url='/static/favicon.ico',
)

admin.admin.add_exception_handler(
    NodeException, node_exception_handler)


app.state.admin = admin

app.include_router(v1_router)

admin.add_model_view(NodeAdmin)
admin.add_model_view(UserAdmin)
admin.add_model_view(ButtonAdmin)
admin.add_model_view(ImageAdmin)
admin.add_model_view(HRRequestAdmin)
