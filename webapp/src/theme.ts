import { createTheme } from '@mantine/core';
import type { MantineColorsTuple } from '@mantine/core';

const electricBlue: MantineColorsTuple = [
  '#e3f6ff',
  '#cde9ff',
  '#9ad0ff',
  '#63b5ff',
  '#389eff',
  '#1d90ff',
  '#0089ff',
  '#0076e4',
  '#0069cc',
  '#005ab4',
];

export const RARITY_COLORS = {
  common: '#9E9E9E',
  rare: '#4FC3F7',
  epic: '#B388FF',
  legendary: '#FF9800',
  mythic: '#FF1744',
} as const;

export const GAME_COLORS = {
  gold: '#FFD700',
  danger: '#FF4444',
  epicPurple: '#B388FF',
  bg: '#0a0e17',
  cardBg: '#111827',
  cardBorder: 'rgba(79, 195, 247, 0.15)',
  primary: '#4FC3F7',
} as const;

export const theme = createTheme({
  primaryColor: 'electricBlue',
  colors: {
    electricBlue,
    dark: [
      '#C1C2C5',
      '#A6A7AB',
      '#909296',
      '#5c5f66',
      '#373A40',
      '#2C2E33',
      '#1A1B1E',
      '#111827',
      '#0d1117',
      '#0a0e17',
    ],
  },
  fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  headings: {
    fontFamily: 'Orbitron, Inter, system-ui, sans-serif',
  },
  defaultRadius: 'md',
  other: {
    gameColors: GAME_COLORS,
    rarityColors: RARITY_COLORS,
  },
});
