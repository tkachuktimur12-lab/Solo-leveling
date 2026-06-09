import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Card, Text, Button, Group, Badge, Loader, Center, SimpleGrid } from '@mantine/core';
import { apiGet, apiPost } from '../api';
import { GAME_COLORS, RARITY_COLORS } from '../theme';

interface ShopItem {
  name: string;
  price: number;
  description?: string;
}

interface BuyResult {
  item: string;
  rarity: string;
  stats?: Record<string, number>;
}

export function ShopPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ShopItem[]>([]);
  const [gold, setGold] = useState(0);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState<string | null>(null);
  const [result, setResult] = useState<BuyResult | null>(null);

  useEffect(() => {
    Promise.all([
      apiGet<{ items: ShopItem[] }>('/api/shop'),
      apiGet<{ gold: number }>('/api/user/stats'),
    ])
      .then(([shop, stats]) => {
        setItems(shop.items ?? (Array.isArray(shop) ? shop as unknown as ShopItem[] : []));
        setGold(stats.gold ?? 0);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const buyItem = async (name: string) => {
    setBuying(name);
    setResult(null);
    try {
      const res = await apiPost<BuyResult>(`/api/shop/buy/${encodeURIComponent(name)}`);
      setResult(res);
      const stats = await apiGet<{ gold: number }>('/api/user/stats');
      setGold(stats.gold ?? 0);
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
          border: `2px solid ${RARITY_COLORS[result.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? RARITY_COLORS.common}`,
          textAlign: 'center',
        }}>
          <Text fw={600}>Purchased!</Text>
          <Text size="sm" style={{ color: RARITY_COLORS[result.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? '#fff' }}>
            {result.item} ({result.rarity})
          </Text>
          {result.stats && Object.keys(result.stats).length > 0 && (
            <Group justify="center" gap={8} mt={4}>
              {Object.entries(result.stats).map(([k, v]) => v > 0 && (
                <Text key={k} size="xs" c="dimmed">{k.toUpperCase()}: +{v}</Text>
              ))}
            </Group>
          )}
        </Card>
      )}

      <SimpleGrid cols={1} spacing="sm">
        {items.map((item) => (
          <Card key={item.name} p="sm" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.cardBorder}` }}>
            <Group justify="space-between" align="center">
              <div>
                <Text size="sm" fw={600}>{item.name}</Text>
                {item.description && <Text size="xs" c="dimmed">{item.description}</Text>}
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
