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

export interface ServerStateUpdate {
  newState: OPCClientState;
}

export interface ServerTimeUpdate {
  newTime: string;
}

// MODEL

export interface VariableValueUpdate {
  entityId: string;
  newValue: any;
}
