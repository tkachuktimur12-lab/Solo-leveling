import { Card, Group, Text, Badge, UnstyledButton } from '@mantine/core';
import { GAME_COLORS } from '../theme';

interface QuestItemProps {
  name: string;
  xp: number;
  completed: boolean;
  disabled?: boolean;
  onComplete?: () => void;
}

export function QuestItem({ name, xp, completed, disabled, onComplete }: QuestItemProps) {
  return (
    <UnstyledButton
      onClick={onComplete}
      disabled={disabled || completed}
      style={{ width: '100%' }}
    >
      <Card
        p="sm"
        style={{
          background: completed
            ? 'rgba(76, 175, 80, 0.08)'
            : GAME_COLORS.cardBg,
          border: `1px solid ${completed ? 'rgba(76,175,80,0.3)' : GAME_COLORS.cardBorder}`,
          opacity: disabled && !completed ? 0.5 : 1,
          cursor: disabled || completed ? 'default' : 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <Group justify="space-between">
          <Group gap="sm">
            <Text size="lg">{completed ? '✅' : '⬜'}</Text>
            <Text
              size="sm"
              fw={500}
              td={completed ? 'line-through' : undefined}
              c={completed ? 'dimmed' : undefined}
            >
              {name}
            </Text>
          </Group>
          <Badge variant="light" color="electricBlue" size="sm">
            +{xp} XP
          </Badge>
        </Group>
      </Card>
    </UnstyledButton>
  );
}
