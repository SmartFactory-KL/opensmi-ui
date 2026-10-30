import type { VariableModifier } from "./NodeFeatureTypes";
import type { LocalizedTextData } from "./OPCTypes";

export enum SkillState {
  HALTED = 11,
  READY = 12,
  RUNNING = 13,
  SUSPENDED = 14,
  COMPLETED = 15,
  STARTING = 16,
  HALTING = 17,
  COMPLETING = 18,
  RESETTING = 19,
  SUSPENDING = 20,
}

export const SkillStateByLabel: Record<string, SkillState> = {
  halted: SkillState.HALTED,
  ready: SkillState.READY,
  running: SkillState.RUNNING,
  suspended: SkillState.SUSPENDED,
  completed: SkillState.COMPLETED,
  starting: SkillState.STARTING,
  halting: SkillState.HALTING,
  completing: SkillState.COMPLETING,
  resetting: SkillState.RESETTING,
  suspending: SkillState.SUSPENDING,
};

export interface ComponentEntityData {
  entityId: string;
  name: string;
  componentType: string;
}

export interface VariableEntityData {
  name: string;
  description: LocalizedTextData;
  dataType: string;
  value: Any;

  lastUpdatedAt: string | null;
  rank: number;
  isWritable: boolean;

  modifiers: VariableModifier[];
}

export interface MachineryItemStateEntityData {
  name: string;
  currentState: LocalizedTextData | null;
}

export interface UserEntityData {
  name: string;
  allowMultiple: boolean;
  currentAccessLevel: number;
  maxAccessLevel: number;
  isPresent: boolean;
}

export interface LockEntityData {
  name: string;

  isLocked: boolean;
  isLockedLastChange: string;

  lockingUser: string;
  lockingUserLastChange: string;

  lockingClient: string;
  lockingClientLastChange: string;
}

export interface SkillControlEntityData {
  name: string;
  currentState: string | number;
  currentStateLastChange: string;
  isSuspendable: boolean;
}

export interface SkillEntityData {
  name: string;
  minAccessLevel: number;
}

export interface DependencyEntityData {
  name: string;
  dependsOn: NodeIdData[];
  dependencyOf: NodeIdData[];
}
