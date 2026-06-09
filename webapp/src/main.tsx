import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { init, mockTelegramEnv } from '@telegram-apps/sdk-react';
import '@mantine/core/styles.css';
import './index.css';
import App from './App';

// Check if we're inside Telegram
const isTelegram = !!(window as any).Telegram?.WebApp?.initData;

try {
  if (isTelegram) {
    init();
  } else if (import.meta.env.DEV) {
    mockTelegramEnv({
      launchParams: {
        tgWebAppVersion: '7.0',
        tgWebAppPlatform: 'tdesktop',
        tgWebAppThemeParams: {
          bg_color: '#0a0e17',
          button_color: '#4FC3F7',
          button_text_color: '#ffffff',
          hint_color: '#909296',
          link_color: '#4FC3F7',
          secondary_bg_color: '#111827',
          text_color: '#C1C2C5',
        },
        tgWebAppData: new URLSearchParams({
          user: JSON.stringify({
            id: 1,
            first_name: 'Dev',
            last_name: 'Hunter',
            username: 'dev_hunter',
            language_code: 'en',
          }),
          hash: 'dev-hash',
          auth_date: String(Math.floor(Date.now() / 1000)),
        }),
      },
    });
    init();
  } else {
    init();
  }
} catch (e) {
  console.error('Telegram SDK init failed:', e);
}

// Expand Mini App to full height
try {
  const tg = (window as any).Telegram?.WebApp;
  tg?.expand();
  tg?.ready();
} catch { /* ignore outside Telegram */ }

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
