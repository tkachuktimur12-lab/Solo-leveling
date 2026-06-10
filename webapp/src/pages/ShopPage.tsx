import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Card, Text, Button, Group, Badge, Loader, Center, SimpleGrid } from '@mantine/core';
import { api, unwrap } from '../api';
import type { BuyResult, ShopItem } from '../api/types';
import { GAME_COLORS, RARITY_COLORS } from '../theme';

const STAT_LABELS: Record<string, string> = {
  strength: 'STR',
  intelligence: 'INT',
  agility: 'AGI',
  vitality: 'VIT',
  sense: 'SENSE',
};

export function ShopPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ShopItem[]>([]);
  const [gold, setGold] = useState(0);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState<string | null>(null);
  const [result, setResult] = useState<BuyResult | null>(null);

  useEffect(() => {
    Promise.all([
      unwrap(api.GET('/api/shop')),
      unwrap(api.GET('/api/user/stats')),
    ])
      .then(([shop, stats]) => {
        setItems(shop.items);
        setGold(stats.gold);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const buyItem = async (name: string) => {
    setBuying(name);
    setResult(null);
    try {
      const res = await unwrap(api.POST('/api/shop/buy/{item_name}', { params: { path: { item_name: name } } }));
      setResult(res);
      setGold(res.gold);
    } catch (e) { console.error(e); }
    finally { setBuying(null); }
  };

  if (loading) {
    return <Center h="80vh"><Loader color="electricBlue" /></Center>;
  }

  return (
    <Stack gap="md">
      <Button variant="subtle" color="gray" size="xs" onClick={() => navigate('/')}>
        ← Back
      </Button>

      <Text size="xl" fw={700} ta="center" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
        🛒 Shop
      </Text>

      <Card p="sm" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.gold}`, textAlign: 'center' }}>
        <Text size="lg" fw={700} style={{ color: GAME_COLORS.gold }}>
          💰 {gold} Gold
        </Text>
      </Card>

      {result && (
        <Card p="sm" style={{
          background: GAME_COLORS.cardBg,
          border: `2px solid ${RARITY_COLORS[result.item.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? RARITY_COLORS.common}`,
          textAlign: 'center',
        }}>
          <Text fw={600}>Purchased!</Text>
          <Text size="sm" style={{ color: RARITY_COLORS[result.item.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? '#fff' }}>
            {result.item.name} ({result.item.rarity})
          </Text>
          <Group justify="center" gap={8} mt={4}>
            {Object.entries(STAT_LABELS).map(([key, label]) => {
              const value = result.item[key as keyof typeof result.item] as number;
              return value > 0 ? (
                <Text key={key} size="xs" c="dimmed">{label}: +{value}</Text>
              ) : null;
            })}
          </Group>
        </Card>
      )}

      <SimpleGrid cols={1} spacing="sm">
        {items.map((item) => (
          <Card key={item.name} p="sm" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.cardBorder}` }}>
            <Group justify="space-between" align="center">
              <div>
                <Text size="sm" fw={600}>{item.name}</Text>
              </div>
              <Group gap="xs">
                <Badge variant="light" color="yellow" size="sm">
                  {item.price}g
                </Badge>
                <Button
                  size="xs"
                  variant="gradient"
                  gradient={{ from: '#FFD700', to: '#FFA000' }}
                  loading={buying === item.name}
                  disabled={gold < item.price}
                  onClick={() => buyItem(item.name)}
                  style={{ color: '#000' }}
                >
                  Buy
                </Button>
              </Group>
            </Group>
          </Card>
        ))}
      </SimpleGrid>
    </Stack>
  );
}
