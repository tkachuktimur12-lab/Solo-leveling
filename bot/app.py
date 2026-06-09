from telegram.ext import ApplicationBuilder

from .config import TOKEN
from .db import init_db
from .handlers import register_handlers


def build_app():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)
    return app
