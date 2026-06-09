import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { init, mockTelegramEnv } from '@telegram-apps/sdk-react';
import '@mantine/core/styles.css';
import './index.css';
import App from './App';

if (import.meta.env.DEV) {
  try {
    init();
  } catch {
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
  }
} else {
  init();
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
