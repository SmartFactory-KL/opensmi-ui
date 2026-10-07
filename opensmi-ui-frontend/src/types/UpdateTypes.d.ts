import type { GenericUpdateMessage } from "./GenericTypes";

type RemoteServerStatus =
  | "DISCONNECTED"
  | "CONNECTING"
  | "BROWSING"
  | "CONNECTED"
  | "RECONNECTING"
  | "DISCONNECTING";

export type ServerStateUpdateMessage = GenericUpdateMessage<RemoteServerStatus>;
export type ServerTimeUpdateMessage = GenericUpdateMessage<string>;

// Machine Stuff
export interface MachineStateUpdate {
  newState: string;
}

export interface MachineNewMessageUpdate {
  severity: number;
  code: string;
  text: string;
}

export interface MachineLockStateUpdate {
  isLocked: boolean;
}

export interface MachineLockUserUpdate {
  newLockingUser: string;
}

// Component Stuff
export interface ComponentStateUpdate {
  newState: string;
}

export interface ComponentNewMessageUpdate {
  severity: number;
  code: string;
  text: string;
}

// Skill Stuff
export interface SkillStateUpdate {
  newState: string;
}

// Variable Stuff
export interface VariableDataValueUpdate extends SimpleDataValueDto {}
