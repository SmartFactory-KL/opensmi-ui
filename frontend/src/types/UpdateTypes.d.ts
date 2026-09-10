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
export type ServerConnectionState =
  | "open"
  | "pending"
  | "connected"
  | "browsing";

export interface ServerConnectionUpdate {
  connectionState: ServerConnectionState;
}

export interface ServerTimeUpdate {
  newDatetime: string;
}

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
