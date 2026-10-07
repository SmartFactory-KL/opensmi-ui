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
