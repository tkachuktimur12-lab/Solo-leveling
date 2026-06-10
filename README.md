# Solo Leveling

Telegram Mini App inspired by Solo Leveling progression systems — a fitness gamification RPG.

## Features
- **Daily Quests**: 5 random fitness exercises, earn XP and streaks
- **Dungeons**: E→S ranked dungeon gates with enemy tasks and boss fights
- **Class System**: Awakening (level 10) and Job Change (level 100)
- **Equipment**: Loot, inventory, and equipment with rarity tiers
- **Stat Allocation**: STR / INT / AGI / VIT / SENSE
- **Hidden & Dungeon Rolls**: Chance-based bonus quests and high-rank dungeons

## Structure
- `game/` — shared game logic (constants, DB, calculations)
- `api/` — FastAPI backend (REST API for the Mini App)
- `webapp/` — React Mini App (Vite + TypeScript + Mantine UI)

## Run the Mini App

### 1. Backend (FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure token
cp .env.example .env
# Set TELEGRAM_BOT_TOKEN=your_token_here

# Start the API server
uvicorn api.main:app --reload --port 8000
```

### 2. Frontend (React)
```bash
cd webapp
npm install
npm run dev
```

The dev server proxies `/api` requests to `http://localhost:8000`.

### 3. Connect to Telegram
1. Open [@BotFather](https://t.me/BotFather)
2. Go to **Bot Settings → Configure Mini App → Edit Mini App URL**
3. Set the URL to your deployed frontend (e.g. your HTTPS tunnel or hosting URL)

## Keeping frontend & backend models in sync
The backend's FastAPI OpenAPI schema is the **single source of truth** for the API contract. The React app's request/response types are generated from it, so a backend model change that isn't reflected in the frontend becomes a TypeScript compile error instead of a silent runtime bug.
Whenever you change an API model (`api/schemas.py`) or a route's `response_model`, regenerate the frontend types:
```bash
cd webapp
npm run gen:api   # writes webapp/openapi.json, then src/api/schema.d.ts
```
`gen:api` runs `scripts/export_openapi.py` (needs the backend deps importable — activate your virtualenv first) followed by `openapi-typescript`. The generated `webapp/openapi.json` and `webapp/src/api/schema.d.ts` are committed so contract changes show up in review.
In the app, use the typed client in `webapp/src/api.ts` (`api.GET` / `api.POST` + `unwrap`) and the aliases in `webapp/src/api/types.ts` instead of hand-writing interfaces.

## Tech Stack
- **Backend**: Python, FastAPI, SQLite
- **Frontend**: React 18, Vite, TypeScript, Mantine v7
- **Telegram**: @telegram-apps/sdk-react, telegram-init-data
- **API types**: OpenAPI (FastAPI) → TypeScript via openapi-typescript + openapi-fetch
