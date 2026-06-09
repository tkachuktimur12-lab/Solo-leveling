import { Group, Text, Progress } from '@mantine/core';

interface StatBarProps {
  icon: string;
  label: string;
  value: number;
  bonus?: number;
  maxValue?: number;
  color?: string;
}

export function StatBar({ icon, label, value, bonus = 0, maxValue, color = '#4FC3F7' }: StatBarProps) {
  const total = value + bonus;
  const pct = maxValue ? (total / maxValue) * 100 : undefined;

  return (
    <div style={{ marginBottom: 8 }}>
      <Group justify="space-between" mb={2}>
        <Group gap={6}>
          <Text size="md">{icon}</Text>
          <Text size="sm" fw={500}>{label}</Text>
        </Group>
        <Text size="sm" fw={700} style={{ color }}>
          {total}
          {bonus > 0 && (
            <Text component="span" size="xs" c="dimmed"> ({value}+{bonus})</Text>
          )}
        </Text>
      </Group>
      {pct !== undefined && (
        <Progress value={Math.min(pct, 100)} size="xs" color={color} />
      )}
    </div>
  );
}
