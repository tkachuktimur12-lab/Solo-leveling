import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Text, Tabs, Loader, Center, Card, Badge, Group } from '@mantine/core';
import { ItemCard } from '../components/ItemCard';
import { api, unwrap } from '../api';
import type { InventoryItem as ApiInventoryItem } from '../api/types';
import { GAME_COLORS, RARITY_COLORS } from '../theme';

// UI-facing shape (normalized from the API row below).
interface InventoryItem {
  id: number;
  name: string;
  rarity: string;
  slot: string;
  stats: Record<string, number>;
  equipped: boolean;
}

interface EquipmentSlot {
  slot: string;
  item: InventoryItem | null;
}

const EQUIPMENT_SLOTS = ['weapon', 'armor', 'charm'] as const;

function toInventoryItem(raw: ApiInventoryItem): InventoryItem {
  return {
    id: raw.item_id,
    name: raw.item_name,
    rarity: raw.rarity,
    slot: raw.slot,
    stats: {
      str: raw.strength,
      int: raw.intelligence,
      agi: raw.agility,
      vit: raw.vitality,
      sense: raw.sense,
    },
    equipped: Boolean(raw.equipped),
  };
}

export function InventoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentSlot[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [inv, equip] = await Promise.all([
        unwrap(api.GET('/api/inventory')),
        unwrap(api.GET('/api/inventory/equipment')),
      ]);
      setItems(inv.items.map(toInventoryItem));
      setEquipment(
        EQUIPMENT_SLOTS.map((slot) => ({
          slot,
          item: equip[slot] ? toInventoryItem(equip[slot] as ApiInventoryItem) : null,
        })),
      );
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const equipItem = async (id: number) => {
    try {
      await unwrap(api.POST('/api/inventory/equip/{item_id}', { params: { path: { item_id: id } } }));
      fetchData();
    } catch (e) { console.error(e); }
  };

  if (loading) {
    return <Center h="80vh"><Loader color="electricBlue" /></Center>;
  }

  const SLOT_ICONS: Record<string, string> = {
    weapon: '⚔️',
    armor: '🛡️',
    charm: '💎',
  };

  return (
    <Stack gap="md">
      <button
        onClick={() => navigate('/')}
        style={{ background: 'none', border: 'none', color: '#909296', cursor: 'pointer', textAlign: 'left', padding: '4px 0', fontSize: 14 }}
      >
        ← Back
      </button>

      <Text size="xl" fw={700} ta="center" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
        🎒 Inventory
      </Text>

      <Tabs defaultValue="items" color="electricBlue">
        <Tabs.List>
          <Tabs.Tab value="items">Items</Tabs.Tab>
          <Tabs.Tab value="equipment">Equipment</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="items" pt="sm">
          {items.length === 0 ? (
            <Text ta="center" c="dimmed" mt="lg">No items yet. Visit the shop or run dungeons!</Text>
          ) : (
            <Stack gap="xs">
              {items.map((item) => (
                <ItemCard
                  key={item.id}
                  id={item.id}
                  name={item.name}
                  rarity={item.rarity}
                  slot={item.slot}
                  stats={item.stats}
                  equipped={item.equipped}
                  onEquip={equipItem}
                />
              ))}
            </Stack>
          )}
        </Tabs.Panel>

        <Tabs.Panel value="equipment" pt="sm">
          <Stack gap="xs">
            {(['weapon', 'armor', 'charm'] as const).map((slot) => {
              const eq = equipment.find((e) => e.slot === slot);
              const item = eq?.item;
              const rarityColor = item
                ? RARITY_COLORS[item.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? RARITY_COLORS.common
                : GAME_COLORS.cardBorder;

              return (
                <Card
                  key={slot}
                  p="sm"
                  style={{
                    background: GAME_COLORS.cardBg,
                    border: `1px solid ${rarityColor}`,
                  }}
                >
                  <Group justify="space-between">
                    <Group gap="xs">
                      <Text size="lg">{SLOT_ICONS[slot] ?? '📦'}</Text>
                      <div>
                        <Text size="xs" c="dimmed" tt="uppercase">{slot}</Text>
                        {item ? (
                          <Text size="sm" fw={600} style={{ color: rarityColor }}>
                            {item.name}
                          </Text>
                        ) : (
                          <Text size="sm" c="dimmed">Empty</Text>
                        )}
                      </div>
                    </Group>
                    {item && (
                      <Badge size="xs" variant="light" style={{ backgroundColor: `${rarityColor}22`, color: rarityColor }}>
                        {item.rarity}
                      </Badge>
                    )}
                  </Group>
                  {item?.stats && Object.keys(item.stats).length > 0 && (
                    <Group gap={8} mt={4}>
                      {Object.entries(item.stats).map(([k, v]) => v > 0 && (
                        <Text key={k} size="xs" c="dimmed">{k.toUpperCase()}: +{v}</Text>
                      ))}
                    </Group>
                  )}
                </Card>
              );
            })}
          </Stack>
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
