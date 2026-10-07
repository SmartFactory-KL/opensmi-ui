export type GenericUpdateEntityType =
  | "Machine"
  | "Server"
  | "Component"
  | "Skill"
  | "Method"
  | "Variable";

export interface GenericUpdateMessage<T> {
  entityId: string; // UUID as a string
  entityType: GenericUpdateEntityType;
  updateType: string;
  updateContent: T;
}
