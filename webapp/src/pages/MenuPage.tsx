import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SimpleGrid, Button, Stack, Text, Loader, Center } from '@mantine/core';
import { HunterCard } from '../components/HunterCard';
import { apiGet } from '../api';
import { GAME_COLORS } from '../theme';

interface UserStats {
  name: string;
  level: number;
  rank: string;
  xp: number;
  xp_needed: number;
}

const MENU_ITEMS = [
  { label: '⚔️ Daily', path: '/daily', gradient: ['#4FC3F7', '#0089ff'] },
  { label: '📊 Stats', path: '/stats', gradient: ['#B388FF', '#7C4DFF'] },
  { label: '🏰 Dungeons', path: '/dungeons', gradient: ['#FF9800', '#F57C00'] },
  { label: '🎲 Roll', path: '/roll', gradient: ['#FF1744', '#D50000'] },
  { label: '🛒 Shop', path: '/shop', gradient: ['#FFD700', '#FFA000'] },
  { label: '🎒 Inventory', path: '/inventory', gradient: ['#4CAF50', '#2E7D32'] },
] as const;

export function MenuPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<UserStats>('/api/user/stats')
      .then(setStats)
      .catch(() => setStats({ name: 'Hunter', level: 1, rank: 'E', xp: 0, xp_needed: 100 }))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Center h="80vh">
        <Loader color="electricBlue" />
      </Center>
    );
  }

  return (
    <Stack gap="md">
      {stats && (
        <HunterCard
          name={stats.name}
          level={stats.level}
          rank={stats.rank}
          xp={stats.xp}
          xpNeeded={stats.xp_needed}
        />
      )}

      <Text
        size="xl"
        fw={700}
        ta="center"
        style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}
      >
        SYSTEM
      </Text>

      <SimpleGrid cols={2} spacing="sm">
        {MENU_ITEMS.map((item) => (
          <Button
            key={item.path}
            size="xl"
            className="glow-btn"
            onClick={() => navigate(item.path)}
            style={{
              background: `linear-gradient(135deg, ${item.gradient[0]}, ${item.gradient[1]})`,
              border: 'none',
              height: 80,
              fontSize: 16,
              fontWeight: 600,
            }}
          >
            {item.label}
          </Button>
        ))}
      </SimpleGrid>
    </Stack>
  );
}
