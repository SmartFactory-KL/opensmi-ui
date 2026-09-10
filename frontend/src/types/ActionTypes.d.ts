// Type for SkillActionType
export type GenericActionType =
  | "WriteParameter"
  | "WriteParameterList"
  | "MethodCall"
  | "SkillStart"
  | "SkillReset"
  | "SkillHalt"
  | "SkillSuspend";

// Base interface for SkillActionDto
export interface GenericActionDto {
  entityId: string; // UUID as a string
  entityType: "Skill" | "Method" | "Component" | "Machine";
  actionType: SkillActionType;
  actionContent: any;
}

// Interface for WriteParameterContent
export interface WriteParameterContent {
  parameterNodeId: string;
  parameterName: string;
  parameterNewValue: string;
}

// Interface for WriteParameterDto
export interface WriteParameterDto extends GenericActionDto {
  actionType: "WriteParameter";
  actionContent: WriteParameterContent;
}
