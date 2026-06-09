"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from game.db import init_db

from .routes import class_, daily, dungeon, inventory, roll, shop, user


def _load_dotenv():
    """Load .env file from project root."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            os.environ.setdefault(key, value)


_load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Solo Leveling API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(daily.router, prefix="/api/daily", tags=["daily"])
app.include_router(dungeon.router, prefix="/api/dungeons", tags=["dungeons"])
app.include_router(roll.router, prefix="/api/roll", tags=["roll"])
app.include_router(shop.router, prefix="/api/shop", tags=["shop"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(class_.router, prefix="/api/class", tags=["class"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
