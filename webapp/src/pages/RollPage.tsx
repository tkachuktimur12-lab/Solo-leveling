import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Card, Text, Button, Group, Loader, Center, Badge } from '@mantine/core';
import { api, unwrap } from '../api';
import type { DungeonRollResult, HiddenRollResult, UserStats } from '../api/types';
import { GAME_COLORS, RARITY_COLORS } from '../theme';

type RollInfo = Pick<UserStats, 'hidden_rolls' | 'dungeon_rolls'>;

export function RollPage() {
  const navigate = useNavigate();
  const [info, setInfo] = useState<RollInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);
  const [hiddenResult, setHiddenResult] = useState<HiddenRollResult | null>(null);
  const [dungeonResult, setDungeonResult] = useState<DungeonRollResult | null>(null);
  const [claimMsg, setClaimMsg] = useState<string | null>(null);

  const fetchInfo = useCallback(async () => {
    try {
      const data = await unwrap(api.GET('/api/user/stats'));
      setInfo({ hidden_rolls: data.hidden_rolls, dungeon_rolls: data.dungeon_rolls });
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchInfo(); }, [fetchInfo]);

  const rollHidden = async () => {
    setActing(true);
    setHiddenResult(null);
    setClaimMsg(null);
    try {
      const res = await unwrap(api.POST('/api/roll/hidden'));
      setHiddenResult(res);
      fetchInfo();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const claimHidden = async (index: number) => {
    setActing(true);
    try {
      const res = await unwrap(api.POST('/api/roll/hidden/claim/{index}', { params: { path: { index } } }));
      setClaimMsg(`Claimed +${res.xp_gained} XP!`);
      setHiddenResult(null);
      fetchInfo();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const rollDungeon = async () => {
    setActing(true);
    setDungeonResult(null);
    try {
      const res = await unwrap(api.POST('/api/roll/dungeon'));
      setDungeonResult(res);
      fetchInfo();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
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
        🎲 Roll
      </Text>

      {/* Hidden Roll */}
      <Card p="md" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.epicPurple}` }}>
        <Text fw={600} mb="xs" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.epicPurple }}>
          Hidden Quest Roll
        </Text>
        <Group justify="space-between" mb="sm">
          <Text size="sm" c="dimmed">Available rolls</Text>
          <Badge variant="filled" color="violet">{info?.hidden_rolls ?? 0}</Badge>
        </Group>
        <Button
          fullWidth
          variant="gradient"
          gradient={{ from: '#B388FF', to: '#7C4DFF' }}
          loading={acting}
          disabled={!info?.hidden_rolls}
          onClick={rollHidden}
        >
          🎲 Roll Hidden Quest
        </Button>

        {hiddenResult && (
          <Card mt="sm" p="sm" style={{
            background: 'rgba(179,136,255,0.08)',
            border: `1px solid ${hiddenResult.found ? GAME_COLORS.epicPurple : GAME_COLORS.cardBorder}`,
          }}>
            {hiddenResult.found && hiddenResult.quest ? (
              <>
                <Text fw={600} ta="center" style={{
                  color: RARITY_COLORS[hiddenResult.quest.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? '#fff',
                }}>
                  {hiddenResult.quest.name}
                </Text>
                <Group justify="center" gap="xs" mt={4}>
                  <Badge size="sm" variant="light" style={{
                    color: RARITY_COLORS[hiddenResult.quest.rarity?.toLowerCase() as keyof typeof RARITY_COLORS] ?? '#fff',
                  }}>
                    {hiddenResult.quest.rarity}
                  </Badge>
                  <Text size="xs" c="dimmed">+{hiddenResult.quest.xp} XP</Text>
                </Group>
                <Button
                  fullWidth
                  mt="sm"
                  variant="light"
                  color="violet"
                  loading={acting}
                  onClick={() => claimHidden(hiddenResult.quest!.index ?? 0)}
                >
                  ✨ Claim Reward
                </Button>
              </>
            ) : (
              <Text ta="center" c="dimmed" size="sm">No hidden quest found this time.</Text>
            )}
          </Card>
        )}

        {claimMsg && (
          <Text ta="center" mt="xs" size="sm" style={{ color: GAME_COLORS.gold }}>
            {claimMsg}
          </Text>
        )}
      </Card>

      {/* Dungeon Roll */}
      <Card p="md" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.primary}` }}>
        <Text fw={600} mb="xs" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
          Dungeon Roll
        </Text>
        <Group justify="space-between" mb="sm">
          <Text size="sm" c="dimmed">Available rolls</Text>
          <Badge variant="filled" color="electricBlue">{info?.dungeon_rolls ?? 0}</Badge>
        </Group>
        <Button
          fullWidth
          variant="gradient"
          gradient={{ from: '#4FC3F7', to: '#0089ff' }}
          loading={acting}
          disabled={!info?.dungeon_rolls}
          onClick={rollDungeon}
        >
          🏰 Roll Dungeon
        </Button>

        {dungeonResult && (
          <Card mt="sm" p="sm" style={{
            background: 'rgba(79,195,247,0.08)',
            border: `1px solid ${dungeonResult.found ? GAME_COLORS.primary : GAME_COLORS.cardBorder}`,
          }}>
            {dungeonResult.found && dungeonResult.gate_rank ? (
              <>
                <Text fw={600} ta="center">
                  {dungeonResult.gate_rank}-Rank Dungeon appeared!
                </Text>
                <Text ta="center" size="sm" c="dimmed">A new gate has opened — enter to challenge it!</Text>
                <Button
                  fullWidth
                  mt="sm"
                  variant="gradient"
                  gradient={{ from: '#FF9800', to: '#F57C00' }}
                  onClick={() => navigate('/dungeons')}
                >
                  🏰 Enter Dungeon
                </Button>
              </>
            ) : (
              <Text ta="center" c="dimmed" size="sm">No dungeon appeared this time.</Text>
            )}
          </Card>
        )}
      </Card>
    </Stack>
  );
}
