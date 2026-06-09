import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Card, Text, Button, Group, Loader, Center, Badge } from '@mantine/core';
import { apiGet, apiPost } from '../api';
import { GAME_COLORS } from '../theme';

interface Stats {
  str: number;
  int: number;
  agi: number;
  vit: number;
  sense: number;
  stat_points: number;
}

const STAT_CONFIG = [
  { key: 'str', label: 'STR', icon: '💪', color: '#4FC3F7' },
  { key: 'int', label: 'INT', icon: '🧠', color: '#B388FF' },
  { key: 'agi', label: 'AGI', icon: '⚡', color: '#FFD700' },
  { key: 'vit', label: 'VIT', icon: '❤️', color: '#FF4444' },
  { key: 'sense', label: 'SENSE', icon: '👁', color: '#FF9800' },
] as const;

export function SpendPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [spending, setSpending] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      const data = await apiGet<Stats>('/api/user/stats');
      setStats(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  const spendPoint = async (stat: string) => {
    setSpending(stat);
    try {
      await apiPost('/api/user/spend', { stat });
      await fetchStats();
    } catch (e) { console.error(e); }
    finally { setSpending(null); }
  };

  if (loading || !stats) {
    return <Center h="80vh"><Loader color="electricBlue" /></Center>;
  }

  return (
    <Stack gap="md">
      <Button variant="subtle" color="gray" size="xs" onClick={() => navigate('/stats')}>
        ← Back to Stats
      </Button>

      <Text size="xl" fw={700} ta="center" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
        Allocate Points
      </Text>

      <Card p="sm" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.primary}`, textAlign: 'center' }}>
        <Text size="lg" fw={700} style={{ color: GAME_COLORS.primary }}>
          Available: <Badge size="lg" variant="filled" color="electricBlue">{stats.stat_points}</Badge>
        </Text>
      </Card>

      <Stack gap="xs">
        {STAT_CONFIG.map(({ key, label, icon, color }) => (
          <Card key={key} p="sm" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.cardBorder}` }}>
            <Group justify="space-between" align="center">
              <Group gap="sm">
                <Text size="lg">{icon}</Text>
                <div>
                  <Text size="sm" fw={600}>{label}</Text>
                  <Text size="xl" fw={700} style={{ color }}>
                    {stats[key as keyof Stats]}
                  </Text>
                </div>
              </Group>
              <Button
                size="md"
                variant="gradient"
                gradient={{ from: color, to: `${color}88` }}
                disabled={stats.stat_points === 0}
                loading={spending === key}
                onClick={() => spendPoint(key)}
                style={{ width: 50, height: 50, padding: 0, fontSize: 24, color: '#000' }}
              >
                +
              </Button>
            </Group>
          </Card>
        ))}
      </Stack>
    </Stack>
  );
}
