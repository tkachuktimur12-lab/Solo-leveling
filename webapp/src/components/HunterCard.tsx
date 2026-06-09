import { Card, Text, Progress, Group, Badge, Stack } from '@mantine/core';
import { GAME_COLORS } from '../theme';

interface HunterCardProps {
  name: string;
  level: number;
  rank: string;
  xp: number;
  xpNeeded: number;
  className?: string;
}

const RANK_COLORS: Record<string, string> = {
  E: '#9E9E9E',
  D: '#4FC3F7',
  C: '#B388FF',
  B: '#FF9800',
  A: '#FF1744',
  S: '#FFD700',
};

export function HunterCard({ name, level, rank, xp, xpNeeded }: HunterCardProps) {
  const pct = xpNeeded > 0 ? (xp / xpNeeded) * 100 : 0;

  return (
    <Card
      p="md"
      style={{
        background: GAME_COLORS.cardBg,
        border: `1px solid ${GAME_COLORS.cardBorder}`,
        boxShadow: '0 0 15px rgba(79,195,247,0.05)',
      }}
    >
      <Group justify="space-between" mb="xs">
        <Text fw={700} size="lg" style={{ fontFamily: 'Orbitron, sans-serif' }}>
          {name}
        </Text>
        <Badge
          size="lg"
          variant="filled"
          color="gray"
          style={{
            backgroundColor: RANK_COLORS[rank] ?? GAME_COLORS.primary,
            color: '#000',
            fontFamily: 'Orbitron, sans-serif',
          }}
        >
          {rank}-Rank
        </Badge>
      </Group>
      <Stack gap={4}>
        <Group justify="space-between">
          <Text size="sm" c="dimmed">Level {level}</Text>
          <Text size="xs" c="dimmed">{xp} / {xpNeeded} XP</Text>
        </Group>
        <Progress value={pct} color="electricBlue" size="sm" animated />
      </Stack>
    </Card>
  );
}
