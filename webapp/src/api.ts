import createClient, { type Middleware } from 'openapi-fetch';
import { retrieveRawInitData } from '@telegram-apps/sdk-react';
import type { paths } from './api/schema';

function getAuthHeader(): string {
  try {
    const raw = retrieveRawInitData();
    if (raw) return `tma ${raw}`;
  } catch { /* SDK not initialized */ }

  // Fallback: read directly from the Telegram WebApp object
  try {
    const initData = (window as Window & {
      Telegram?: { WebApp?: { initData?: string } };
    }).Telegram?.WebApp?.initData;
    if (initData) return `tma ${initData}`;
  } catch { /* not in Telegram */ }

  return '';
}

const authMiddleware: Middleware = {
  onRequest({ request }) {
    const auth = getAuthHeader();
    if (auth) request.headers.set('Authorization', auth);
    return request;
  },
};

/**
 * Fully typed API client. Paths, params, request bodies and responses are all
 * derived from the backend's OpenAPI schema (`./api/schema`), which is
 * generated from the FastAPI app. Run `npm run gen:api` after changing the
 * backend models to refresh the types.
 */
export const api = createClient<paths>();
api.use(authMiddleware);

type FetchLikeResult = { data?: unknown; error?: unknown; response: Response };

/**
 * Unwrap an openapi-fetch result: return the typed `data` on success, or throw
 * on a non-2xx response (preserving the previous throw-based call sites).
 *
 * The result object is inferred as a whole (`R`) and the success type is read
 * off `R['data']`, which preserves precise shapes such as tuples instead of
 * widening them through generic parameter inference.
 */
export async function unwrap<R extends FetchLikeResult>(
  promise: Promise<R>,
): Promise<NonNullable<R['data']>> {
  const { data, error, response } = await promise;
  if (!response.ok || error !== undefined) {
    const detail =
      error && typeof error === 'object' && 'detail' in error
        ? (error as { detail?: unknown }).detail
        : error;
    const message =
      typeof detail === 'string' ? detail : JSON.stringify(detail ?? '');
    throw new Error(`API ${response.status}: ${message}`);
  }
  return data as NonNullable<R['data']>;
}
