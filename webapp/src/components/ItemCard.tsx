import { Card, Text, Group, Badge, Button, Stack } from '@mantine/core';
import { RARITY_COLORS, GAME_COLORS } from '../theme';

interface ItemCardProps {
  id?: number;
  name: string;
  rarity: string;
  slot?: string;
  stats?: Record<string, number>;
  equipped?: boolean;
  onEquip?: (id: number) => void;
}

export function ItemCard({ id, name, rarity, slot, stats, equipped, onEquip }: ItemCardProps) {
  const rarityKey = rarity?.toLowerCase() as keyof typeof RARITY_COLORS;
  const borderColor = RARITY_COLORS[rarityKey] ?? RARITY_COLORS.common;

  return (
    <Card
      p="sm"
      style={{
        background: GAME_COLORS.cardBg,
        border: `2px solid ${borderColor}`,
        boxShadow: `0 0 10px ${borderColor}33`,
      }}
    >
      <Stack gap={4}>
        <Group justify="space-between">
          <Text size="sm" fw={600} style={{ color: borderColor }}>
            {name}
          </Text>
          <Badge size="xs" variant="light" style={{ backgroundColor: `${borderColor}22`, color: borderColor }}>
            {rarity}
          </Badge>
        </Group>
        {slot && (
          <Text size="xs" c="dimmed">Slot: {slot}</Text>
        )}
        {stats && Object.keys(stats).length > 0 && (
          <Group gap={8}>
            {Object.entries(stats).map(([key, val]) => (
              val > 0 && (
                <Text key={key} size="xs" c="dimmed">
                  {key.toUpperCase()}: +{val}
                </Text>
              )
            ))}
          </Group>
        )}
        {onEquip && id !== undefined && !equipped && (
          <Button
            size="xs"
            variant="light"
            color="electricBlue"
            onClick={() => onEquip(id)}
            mt={4}
          >
            Equip
          </Button>
        )}
        {equipped && (
          <Badge size="xs" color="green" variant="filled">Equipped</Badge>
        )}
      </Stack>
    </Card>
  );
}
