import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Card, Text, Group, Badge, Button, Loader, Center, Divider } from '@mantine/core';
import { HunterCard } from '../components/HunterCard';
import { StatBar } from '../components/StatBar';
import { api, unwrap } from '../api';
import type { UserStats } from '../api/types';
import { GAME_COLORS } from '../theme';

export function StatsPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    unwrap(api.GET('/api/user/stats'))
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) {
    return <Center h="80vh"><Loader color="electricBlue" /></Center>;
  }

  const bonuses = stats.equipped_bonuses;

  return (
    <Stack gap="md">
      <Button variant="subtle" color="gray" size="xs" onClick={() => navigate('/')}>
        ← Back
      </Button>

      <HunterCard
        name={stats.name}
        level={stats.level}
        rank={stats.rank}
        xp={stats.xp}
        xpNeeded={stats.xp_needed}
      />

      <Card p="md" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.cardBorder}` }}>
        <Text fw={600} mb="sm" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
          Combat Stats
        </Text>
        <StatBar icon="💪" label="STR" value={stats.str} bonus={bonuses.str ?? 0} />
        <StatBar icon="🧠" label="INT" value={stats.int} bonus={bonuses.int ?? 0} color="#B388FF" />
        <StatBar icon="⚡" label="AGI" value={stats.agi} bonus={bonuses.agi ?? 0} color="#FFD700" />
        <StatBar icon="❤️" label="VIT" value={stats.vit} bonus={bonuses.vit ?? 0} color="#FF4444" />
        <StatBar icon="👁" label="SENSE" value={stats.sense} bonus={bonuses.sense ?? 0} color="#FF9800" />

        {stats.stat_points > 0 && (
          <Button
            fullWidth
            mt="sm"
            variant="gradient"
            gradient={{ from: '#4FC3F7', to: '#0089ff' }}
            onClick={() => navigate('/spend')}
          >
            Allocate {stats.stat_points} Points
          </Button>
        )}
      </Card>

      <Card p="md" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.cardBorder}` }}>
        <Text fw={600} mb="sm" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
          Hunter Info
        </Text>
        <Group justify="space-between" mb={4}>
          <Text size="sm" c="dimmed">🔥 Streak</Text>
          <Text size="sm" fw={600}>{stats.streak}</Text>
        </Group>
        <Group justify="space-between" mb={4}>
          <Text size="sm" c="dimmed">🎲 Hidden Rolls</Text>
          <Text size="sm" fw={600}>{stats.hidden_rolls}</Text>
        </Group>
        <Group justify="space-between" mb={4}>
          <Text size="sm" c="dimmed">🏰 Dungeon Rolls</Text>
          <Text size="sm" fw={600}>{stats.dungeon_rolls}</Text>
        </Group>
        <Group justify="space-between" mb={4}>
          <Text size="sm" c="dimmed">💰 Gold</Text>
          <Text size="sm" fw={600} style={{ color: GAME_COLORS.gold }}>{stats.gold}</Text>
        </Group>

        <Divider my="sm" color="dark.4" />

        <Group justify="space-between" mb={4}>
          <Text size="sm" c="dimmed">Awakening Class</Text>
          <Badge variant="light" color={stats.awakening_class ? 'electricBlue' : 'gray'}>
            {stats.awakening_class ?? 'None'}
          </Badge>
        </Group>
        <Group justify="space-between">
          <Text size="sm" c="dimmed">Job Class</Text>
          <Badge variant="light" color={stats.job_class ? 'violet' : 'gray'}>
            {stats.job_class ?? 'None'}
          </Badge>
        </Group>
      </Card>
    </Stack>
  );
}
