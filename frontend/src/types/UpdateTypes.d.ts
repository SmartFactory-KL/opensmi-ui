export type GenericUpdateEntityType =
  | "Machine"
  | "Server"
  | "Component"
  | "Skill"
  | "Method"
  | "Variable";

export interface GenericUpdateMessage {
  entityId: string; // UUID as a string
  entityType: GenericUpdateEntityType;
  updateType: string;
  updateContent: any;
}

// Server Stuff
// ##############################################################
type RemoteServerStatus =
  | "DISCONNECTED"
  | "CONNECTING"
  | "BROWSING"
  | "CONNECTED"
  | "RECONNECTING"
  | "DISCONNECTING";

export type ServerStateUpdateMessage = RemoteServerStatus
export type ServerTimeUpdateMessage = string

export interface ServerPinGuardStateUpdate {
  newIsLocked: boolean;
}
// Machine Stuff
// ##############################################################
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
// ##############################################################
export interface ComponentStateUpdate {
  newState: string;
}

export interface ComponentNewMessageUpdate {
  severity: number;
  code: string;
  text: string;
}

// Skill Stuff
// ##############################################################
export interface SkillStateUpdate {
  newState: string;
}

// Variable Stuff
// ##############################################################
export interface VariableDataValueUpdate extends SimpleDataValueDto {}
