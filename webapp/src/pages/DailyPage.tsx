import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Button, Text, Card, Loader, Center, Alert } from '@mantine/core';
import { QuestItem } from '../components/QuestItem';
import { api, unwrap } from '../api';
import type { ClaimResult, DailyState } from '../api/types';
import { GAME_COLORS } from '../theme';

export function DailyPage() {
  const navigate = useNavigate();
  const [daily, setDaily] = useState<DailyState | null>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);
  const [claimResult, setClaimResult] = useState<ClaimResult | null>(null);

  const fetchDaily = useCallback(() => {
    setLoading(true);
    unwrap(api.GET('/api/daily'))
      .then(setDaily)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchDaily(); }, [fetchDaily]);

  const startDaily = async () => {
    setActing(true);
    try {
      await unwrap(api.POST('/api/daily/start'));
      fetchDaily();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const completeTask = async (index: number) => {
    setActing(true);
    try {
      await unwrap(api.POST('/api/daily/task/{index}', { params: { path: { index } } }));
      fetchDaily();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const claimReward = async () => {
    setActing(true);
    try {
      const result = await unwrap(api.POST('/api/daily/claim'));
      setClaimResult(result);
      fetchDaily();
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
        ⚔️ Daily Quests
      </Text>

      {daily?.cooldown_active && (
        <Alert color="yellow" variant="light">
          Daily quests on cooldown.{' '}
          {daily.cooldown_remaining > 0 &&
            `Resets in: ${Math.floor(daily.cooldown_remaining / 3600)}h ${Math.floor((daily.cooldown_remaining % 3600) / 60)}m`}
        </Alert>
      )}

      {(!daily?.active_quests || daily.active_quests.length === 0) && !daily?.cooldown_active && (
        <Button
          size="lg"
          fullWidth
          loading={acting}
          variant="gradient"
          gradient={{ from: '#4FC3F7', to: '#0089ff' }}
          onClick={startDaily}
        >
          Start Daily Quests
        </Button>
      )}

      {daily?.active_quests && daily.active_quests.length > 0 && (
        <Stack gap="xs">
          {daily.active_quests.map((quest, i) => {
            const completed = i < (daily.quest_progress ?? 0);
            const canDo = i === (daily.quest_progress ?? 0);
            return (
              <QuestItem
                key={i}
                name={quest.name}
                xp={quest.xp}
                completed={completed}
                disabled={!canDo || acting}
                onComplete={() => completeTask(i)}
              />
            );
          })}
        </Stack>
      )}

      {daily && daily.quest_progress >= 5 && !claimResult && (
        <Button
          size="lg"
          fullWidth
          loading={acting}
          variant="gradient"
          gradient={{ from: '#FFD700', to: '#FFA000' }}
          onClick={claimReward}
        >
          🎁 Claim Reward
        </Button>
      )}

      {claimResult && (
        <Card p="md" style={{ background: GAME_COLORS.cardBg, border: `1px solid ${GAME_COLORS.gold}` }}>
          <Text fw={600} ta="center" style={{ color: GAME_COLORS.gold, fontFamily: 'Orbitron, sans-serif' }}>
            Rewards Claimed!
          </Text>
          <Text ta="center" mt="xs">+{claimResult.xp_gained} XP</Text>
          <Text ta="center" size="sm" c="dimmed">🔥 Streak: {claimResult.streak}</Text>
          {claimResult.level_ups > 0 && (
            <Text ta="center" size="sm" mt="xs" style={{ color: GAME_COLORS.primary }}>
              ⬆️ Level Up! Now level {claimResult.level}
            </Text>
          )}
        </Card>
      )}
    </Stack>
  );
}
