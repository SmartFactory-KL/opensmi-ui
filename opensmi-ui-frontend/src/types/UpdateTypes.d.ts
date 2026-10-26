import type { OPCSessionData } from "@/stores/ServerSessionStore";
import type { GenericUpdateMessage } from "./GenericTypes";

type OPCClientState =
  | "disconnected"
  | "connecting"
  | "socket_open"
  | "channel_open"
  | "connected"
  | "reconnecting"
  | "disconnecting";

// SERVER

export interface ServerSessionUpdate {
  newSession: OPCSessionData;
}

export interface ServerTimeUpdate {
  newTime: string;
}

// MODEL

export interface VariableValueUpdate {
  entityId: string;
  newValue: any;
}

export interface LockIsLockedUpdate {
  entityId: string;
  timestamp: string;
  newIsLocked: boolean;
}

export interface LockLockingUserUpdate {
  entityId: string;
  timestamp: string;
  newUser: string;
}

export interface LockLockingClientUpdate {
  entityId: string;
  timestamp: string;
  newClient: string;
}

export interface SkillControlStateUpdate {
  entityId: string;
  newState: string | number;
  timestamp: string;
}

// ACTIONS
export interface GenericAction {
  entityId: string;
  action: any;
  actionType: string;
}

export interface LockAction {
  requestedAction: "InitLock" | "BreakLock" | "ExitLock";
}

export interface SkillControlAction {
  requestedAction: "Start" | "Halt" | "Reset" | "Suspend";
}
