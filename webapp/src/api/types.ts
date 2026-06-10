/**
 * Convenience aliases for the auto-generated OpenAPI component schemas.
 *
 * Import these instead of hand-writing request/response interfaces so the
 * frontend stays in lockstep with the backend contract. Regenerate the
 * underlying `schema.d.ts` with `npm run gen:api` after changing API models.
 */
import type { components } from './schema';

type Schemas = components['schemas'];

export type StatBlock = Schemas['StatBlock'];
export type Enemy = Schemas['Enemy'];

export type UserStats = Schemas['UserStats'];
export type SpendResult = Schemas['SpendResult'];

export type DailyState = Schemas['DailyState'];
export type DailyStartResult = Schemas['DailyStartResult'];
export type TaskProgress = Schemas['TaskProgress'];
export type ClaimResult = Schemas['ClaimResult'];

export type DungeonList = Schemas['DungeonList'];
export type EnterDungeon = Schemas['EnterDungeon'];
export type DungeonTask = Schemas['DungeonTask'];
export type BossRoom = Schemas['BossRoom'];
export type BossDefeat = Schemas['BossDefeat'];
export type LootItem = Schemas['LootItem'];

export type HiddenQuest = Schemas['HiddenQuest'];
export type HiddenRollResult = Schemas['HiddenRollResult'];
export type HiddenClaimResult = Schemas['HiddenClaimResult'];
export type DungeonRollResult = Schemas['DungeonRollResult'];

export type ShopItem = Schemas['ShopItem'];
export type ShopList = Schemas['ShopList'];
export type BoughtItem = Schemas['BoughtItem'];
export type BuyResult = Schemas['BuyResult'];

export type InventoryItem = Schemas['InventoryItem'];
export type InventoryList = Schemas['InventoryList'];
export type Equipment = Schemas['Equipment'];
export type EquipResult = Schemas['EquipResult'];

export type AwakeningResult = Schemas['AwakeningResult'];
export type JobChangeResult = Schemas['JobChangeResult'];
