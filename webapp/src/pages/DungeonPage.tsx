import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Button, Text, Card, Group, Badge } from '@mantine/core';
import { QuestItem } from '../components/QuestItem';
import { api, unwrap } from '../api';
import type { BossDefeat, Enemy } from '../api/types';
import { GAME_COLORS } from '../theme';

const RANK_OPTS = [
  { rank: 'E', color: '#9E9E9E', label: 'E-Rank' },
  { rank: 'D', color: '#4FC3F7', label: 'D-Rank' },
  { rank: 'C', color: '#B388FF', label: 'C-Rank' },
];

export function DungeonPage() {
  const navigate = useNavigate();
  const [phase, setPhase] = useState<'select' | 'tasks' | 'boss' | 'victory'>('select');
  const [acting, setActing] = useState(false);
  const [timer, setTimer] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Dungeon state
  const [rank, setRank] = useState('');
  const [enemies, setEnemies] = useState<Enemy[]>([]);
  const [progress, setProgress] = useState(0);
  const [boss, setBoss] = useState<Enemy | null>(null);
  const [rewards, setRewards] = useState<BossDefeat | null>(null);

  const startTimer = useCallback((seconds: number) => {
    setTimer(seconds);
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimer((t) => {
        if (t <= 1) {
          if (timerRef.current) clearInterval(timerRef.current);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
  }, []);

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

  const enterDungeon = async (r: string) => {
    setActing(true);
    try {
      const data = await unwrap(api.POST('/api/dungeons/enter/{rank}', { params: { path: { rank: r } } }));
      setRank(data.rank);
      setEnemies(data.enemies);
      setProgress(0);
      setBoss(null);
      setRewards(null);
      setPhase('tasks');
      startTimer(data.time_limit);
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const completeTask = async (index: number) => {
    setActing(true);
    try {
      const data = await unwrap(api.POST('/api/dungeons/task/{index}', { params: { path: { index } } }));
      setProgress(data.dungeon_progress);
      if (data.boss_available) {
        // Auto-enter boss room
        const bossData = await unwrap(api.POST('/api/dungeons/boss'));
        setBoss(bossData.boss);
        setPhase('boss');
        startTimer(bossData.time_left);
      }
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const defeatBoss = async () => {
    setActing(true);
    try {
      const data = await unwrap(api.POST('/api/dungeons/boss/defeat'));
      setRewards(data);
      setPhase('victory');
      if (timerRef.current) clearInterval(timerRef.current);
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const formatTime = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  return (
    <Stack gap="md">
      <Button variant="subtle" color="gray" size="xs" onClick={() => navigate('/')}>
        ← Back
      </Button>

      <Text size="xl" fw={700} ta="center" style={{ fontFamily: 'Orbitron, sans-serif', color: GAME_COLORS.primary }}>
        🏰 Dungeons
      </Text>

      {phase === 'select' && (
        <Stack gap="sm">
          <Text ta="center" c="dimmed" size="sm">Select dungeon rank</Text>
          {RANK_OPTS.map((opt) => (
            <Button
              key={opt.rank}
              size="lg"
              fullWidth
              loading={acting}
              className="glow-btn"
              style={{
                background: `linear-gradient(135deg, ${opt.color}, ${opt.color}88)`,
                border: 'none',
                color: '#000',
                fontWeight: 700,
              }}
              onClick={() => enterDungeon(opt.rank)}
            >
              {opt.label} Dungeon
            </Button>
          ))}
        </Stack>
      )}

      {(phase === 'tasks' || phase === 'boss') && (
        <>
          <Group justify="space-between">
            <Badge size="lg" variant="filled" color={timer < 30 ? 'red' : 'blue'}>
              ⏱ {formatTime(timer)}
            </Badge>
            <Badge size="lg" variant="light" color="gray">
              {rank}-Rank
            </Badge>
          </Group>

          {phase === 'tasks' && (
            <Stack gap="xs">
              <Text fw={600} size="sm" c="dimmed">Defeat the enemies:</Text>
              {enemies.map((enemy, i) => (
                <QuestItem
                  key={i}
                  name={`${enemy.name} — ${enemy.task}`}
                  xp={0}
                  completed={i < progress}
                  disabled={i !== progress || acting}
                  onComplete={() => completeTask(i)}
                />
              ))}
            </Stack>
          )}

          {phase === 'boss' && boss && (
            <Card p="lg" style={{ background: GAME_COLORS.cardBg, border: `2px solid ${GAME_COLORS.danger}`, textAlign: 'center' }}>
              <Text size="xl" fw={700} style={{ color: GAME_COLORS.danger, fontFamily: 'Orbitron, sans-serif' }}>
                ⚠️ BOSS ROOM
              </Text>
              <Text mt="sm" fw={600}>{boss.name}</Text>
              <Text size="sm" c="dimmed" mt={4}>Task: {boss.task}</Text>
              <Button
                mt="md"
                fullWidth
                variant="gradient"
                gradient={{ from: '#FF4444', to: '#D50000' }}
                loading={acting}
                onClick={defeatBoss}
              >
                ⚔️ Defeat Boss
              </Button>
            </Card>
          )}
        </>
      )}

      {phase === 'victory' && rewards && (
        <Card p="lg" style={{ background: GAME_COLORS.cardBg, border: `2px solid ${GAME_COLORS.gold}`, textAlign: 'center' }}>
          <Text size="xl" fw={700} style={{ color: GAME_COLORS.gold, fontFamily: 'Orbitron, sans-serif' }}>
            🏆 VICTORY!
          </Text>
          <Text mt="sm">+{rewards.xp_reward} XP</Text>
          <Text style={{ color: GAME_COLORS.gold }}>+{rewards.gold_reward} Gold</Text>
          {rewards.loot && (
            <Text mt="xs" style={{ color: GAME_COLORS.epicPurple }}>
              🎁 Loot: {rewards.loot.rarity.toUpperCase()} {rewards.loot.item_name}
            </Text>
          )}
          <Button mt="md" variant="light" color="electricBlue" onClick={() => { setPhase('select'); setRewards(null); }}>
            Continue
          </Button>
        </Card>
      )}
    </Stack>
  );
}
