import { Component, type ReactNode } from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { theme } from './theme';
import { MenuPage } from './pages/MenuPage';
import { StatsPage } from './pages/StatsPage';
import { DailyPage } from './pages/DailyPage';
import { DungeonPage } from './pages/DungeonPage';
import { ShopPage } from './pages/ShopPage';
import { InventoryPage } from './pages/InventoryPage';
import { SpendPage } from './pages/SpendPage';
import { RollPage } from './pages/RollPage';

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 20, color: '#FF4444', background: '#0a0e17', minHeight: '100vh' }}>
          <h2 style={{ color: '#4FC3F7' }}>⚠️ App Error</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{this.state.error.message}</pre>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 10, color: '#909296' }}>{this.state.error.stack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <MantineProvider theme={theme} defaultColorScheme="dark">
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<MenuPage />} />
            <Route path="/stats" element={<StatsPage />} />
            <Route path="/daily" element={<DailyPage />} />
            <Route path="/dungeons" element={<DungeonPage />} />
            <Route path="/shop" element={<ShopPage />} />
            <Route path="/inventory" element={<InventoryPage />} />
            <Route path="/spend" element={<SpendPage />} />
            <Route path="/roll" element={<RollPage />} />
        </Routes>
      </BrowserRouter>
      </MantineProvider>
    </ErrorBoundary>
  );
}
