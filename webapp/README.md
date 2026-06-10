# Solo Leveling — Mini App (web)

React + Vite + TypeScript + Mantine frontend for the Solo Leveling Telegram Mini App.

## Develop

```bash
npm install
npm run dev      # Vite dev server; proxies /api to http://localhost:8000
npm run build    # type-check (tsc -b) + production build
npm run lint
```

## API types are generated — don't hand-write them

All request/response types come from the backend's FastAPI OpenAPI schema, which
is the single source of truth for the API contract.

- `npm run gen:api` exports `openapi.json` from the FastAPI app and regenerates
  `src/api/schema.d.ts`. Run it after any change to `api/schemas.py` or a route's
  `response_model`. It shells out to `../scripts/export_openapi.py`, so the
  backend Python dependencies must be importable (activate the project
  virtualenv first). To only regenerate types from an existing `openapi.json`,
  run `npm run gen:types`.
- `src/api.ts` exposes a typed [`openapi-fetch`](https://openapi-ts.dev/openapi-fetch/)
  client (`api`) plus an `unwrap` helper that returns the typed `data` or throws
  on a non-2xx response. The Telegram `tma` auth header is injected via
  middleware.
- `src/api/types.ts` re-exports friendly aliases for the generated component
  schemas (e.g. `UserStats`, `DailyState`, `BossDefeat`).

### Example

```ts
import { api, unwrap } from './api';
import type { UserStats } from './api/types';

// GET with no params
const stats: UserStats = await unwrap(api.GET('/api/user/stats'));

// Path params + request body are type-checked against the schema
await unwrap(api.POST('/api/dungeons/enter/{rank}', {
  params: { path: { rank: 'E' } },
}));
await unwrap(api.POST('/api/user/spend', { body: { stat: 'str' } }));
```

The generated `openapi.json` and `src/api/schema.d.ts` are committed so contract
changes are visible in code review. If you change a backend model and forget to
regenerate, the mismatch surfaces as a `tsc` error here rather than a runtime bug.
