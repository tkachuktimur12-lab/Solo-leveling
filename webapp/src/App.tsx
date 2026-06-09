import { MantineProvider } from '@mantine/core';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { theme } from './theme';
import { MenuPage } from './pages/MenuPage';
import { StatsPage } from './pages/StatsPage';
import { DailyPage } from './pages/DailyPage';
import { DungeonPage } from './pages/DungeonPage';
import { ShopPage } from './pages/ShopPage';
import { InventoryPage } from './pages/InventoryPage';
import { SpendPage } from './pages/SpendPage';
import { RollPage } from './pages/RollPage';

export default function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <HashRouter>
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
      </HashRouter>
    </MantineProvider>
  );
}
