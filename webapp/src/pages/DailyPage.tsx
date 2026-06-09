import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Button, Text, Card, Loader, Center, Alert } from '@mantine/core';
import { QuestItem } from '../components/QuestItem';
import { apiGet, apiPost } from '../api';
import { GAME_COLORS } from '../theme';

interface Quest {
  name: string;
  xp: number;
}

interface DailyState {
  active: boolean;
  quests: Quest[];
  completed: boolean[];
  all_done: boolean;
  claimed: boolean;
  cooldown?: boolean;
  cooldown_remaining?: string;
}

interface ClaimResult {
  xp_gained: number;
  streak: number;
  hidden_quest?: string;
}

export function DailyPage() {
  const navigate = useNavigate();
  const [daily, setDaily] = useState<DailyState | null>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);
  const [claimResult, setClaimResult] = useState<ClaimResult | null>(null);

  const fetchDaily = useCallback(() => {
    setLoading(true);
    apiGet<DailyState>('/api/daily')
      .then(setDaily)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchDaily(); }, [fetchDaily]);

  const startDaily = async () => {
    setActing(true);
    try {
      await apiPost('/api/daily/start');
      fetchDaily();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const completeTask = async (index: number) => {
    setActing(true);
    try {
      await apiPost(`/api/daily/task/${index}`);
      fetchDaily();
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const claimReward = async () => {
    setActing(true);
    try {
      const result = await apiPost<ClaimResult>('/api/daily/claim');
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

      {daily?.cooldown && (
        <Alert color="yellow" variant="light">
          Daily quests on cooldown. {daily.cooldown_remaining && `Resets in: ${daily.cooldown_remaining}`}
        </Alert>
      )}

      {!daily?.active && !daily?.cooldown && (
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

      {daily?.active && daily.quests && (
        <Stack gap="xs">
          {daily.quests.map((quest, i) => {
            const completed = daily.completed?.[i] ?? false;
            const prevDone = i === 0 || (daily.completed?.[i - 1] ?? false);
            return (
              <QuestItem
                key={i}
                name={quest.name}
                xp={quest.xp}
                completed={completed}
                disabled={!prevDone || acting}
                onComplete={() => completeTask(i)}
              />
            );
          })}
        </Stack>
      )}

      {daily?.all_done && !daily?.claimed && (
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
          {claimResult.hidden_quest && (
            <Text ta="center" size="sm" mt="xs" style={{ color: GAME_COLORS.epicPurple }}>
              🎲 Hidden quest discovered: {claimResult.hidden_quest}
            </Text>
          )}
        </Card>
      )}
    </Stack>
  );
}
