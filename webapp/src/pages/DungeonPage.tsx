import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Button, Text, Card, Group, Loader, Center, Badge } from '@mantine/core';
import { QuestItem } from '../components/QuestItem';
import { apiPost } from '../api';
import { GAME_COLORS } from '../theme';

interface Enemy {
  name: string;
  xp: number;
}

interface Boss {
  name: string;
  task: string;
}

interface DungeonData {
  rank: string;
  enemies: Enemy[];
  completed: boolean[];
  boss: Boss;
  boss_defeated: boolean;
  time_limit: number;
  rewards?: { xp: number; gold: number; loot?: string };
}

const RANK_OPTS = [
  { rank: 'E', color: '#9E9E9E', label: 'E-Rank' },
  { rank: 'D', color: '#4FC3F7', label: 'D-Rank' },
  { rank: 'C', color: '#B388FF', label: 'C-Rank' },
];

export function DungeonPage() {
  const navigate = useNavigate();
  const [dungeon, setDungeon] = useState<DungeonData | null>(null);
  const [phase, setPhase] = useState<'select' | 'tasks' | 'boss' | 'victory'>('select');
  const [acting, setActing] = useState(false);
  const [timer, setTimer] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

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

  const enterDungeon = async (rank: string) => {
    setActing(true);
    try {
      const data = await apiPost<DungeonData>(`/api/dungeons/enter/${rank}`);
      setDungeon(data);
      setPhase('tasks');
      startTimer(data.time_limit);
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const completeTask = async (index: number) => {
    setActing(true);
    try {
      const data = await apiPost<DungeonData>(`/api/dungeons/task/${index}`);
      setDungeon(data);
      const allDone = data.completed.every(Boolean);
      if (allDone) setPhase('boss');
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const enterBoss = async () => {
    setActing(true);
    try {
      await apiPost('/api/dungeons/boss');
    } catch (e) { console.error(e); }
    finally { setActing(false); }
  };

  const defeatBoss = async () => {
    setActing(true);
    try {
      const data = await apiPost<DungeonData>('/api/dungeons/boss/defeat');
      setDungeon(data);
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

      {(phase === 'tasks' || phase === 'boss') && dungeon && (
        <>
          <Group justify="space-between">
            <Badge size="lg" variant="filled" color={timer < 30 ? 'red' : 'blue'}>
              ⏱ {formatTime(timer)}
            </Badge>
            <Badge size="lg" variant="light" color="gray">
              {dungeon.rank}-Rank
            </Badge>
          </Group>

          {phase === 'tasks' && (
            <Stack gap="xs">
              <Text fw={600} size="sm" c="dimmed">Defeat the enemies:</Text>
              {dungeon.enemies.map((enemy, i) => {
                const completed = dungeon.completed?.[i] ?? false;
                const prevDone = i === 0 || (dungeon.completed?.[i - 1] ?? false);
                return (
                  <QuestItem
                    key={i}
                    name={enemy.name}
                    xp={enemy.xp}
                    completed={completed}
                    disabled={!prevDone || acting}
                    onComplete={() => completeTask(i)}
                  />
                );
              })}
            </Stack>
          )}

          {phase === 'boss' && (
            <Card p="lg" style={{ background: GAME_COLORS.cardBg, border: `2px solid ${GAME_COLORS.danger}`, textAlign: 'center' }}>
              <Text size="xl" fw={700} style={{ color: GAME_COLORS.danger, fontFamily: 'Orbitron, sans-serif' }}>
                ⚠️ BOSS ROOM
              </Text>
              <Text mt="sm" fw={600}>{dungeon.boss.name}</Text>
              <Text size="sm" c="dimmed" mt={4}>{dungeon.boss.task}</Text>
              <Group justify="center" mt="md" gap="sm">
                <Button
                  variant="outline"
                  color="red"
                  loading={acting}
                  onClick={enterBoss}
                >
                  Enter Boss Room
                </Button>
                <Button
                  variant="gradient"
                  gradient={{ from: '#FF4444', to: '#D50000' }}
                  loading={acting}
                  onClick={defeatBoss}
                >
                  ⚔️ Defeat Boss
                </Button>
              </Group>
            </Card>
          )}
        </>
      )}

      {phase === 'victory' && dungeon?.rewards && (
        <Card p="lg" style={{ background: GAME_COLORS.cardBg, border: `2px solid ${GAME_COLORS.gold}`, textAlign: 'center' }}>
          <Text size="xl" fw={700} style={{ color: GAME_COLORS.gold, fontFamily: 'Orbitron, sans-serif' }}>
            🏆 VICTORY!
          </Text>
          <Text mt="sm">+{dungeon.rewards.xp} XP</Text>
          <Text style={{ color: GAME_COLORS.gold }}>+{dungeon.rewards.gold} Gold</Text>
          {dungeon.rewards.loot && (
            <Text mt="xs" style={{ color: GAME_COLORS.epicPurple }}>
              🎁 Loot: {dungeon.rewards.loot}
            </Text>
          )}
          <Button mt="md" variant="light" color="electricBlue" onClick={() => setPhase('select')}>
            Continue
          </Button>
        </Card>
      )}

      {phase === 'victory' && !dungeon?.rewards && (
        <Center>
          <Loader color="electricBlue" />
        </Center>
      )}
    </Stack>
  );
}
