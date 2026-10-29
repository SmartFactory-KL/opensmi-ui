export interface OPCNode {
  nodeId: NodeIdData;
  nodeClass: string;
  browseName: QualifiedNameData;
  displayName: LocalizedTextData;
  opcType: QualifiedNameData;
  typeDefinition: NodeIdData | null;
  referenceTypeId: NodeIdData | null;
  attributes: { [key: string]: string };
  properties: { [key: string]: string };
  references: ReferenceData[];
}

export type FeatureInitState = "open" | "pending" | "done" | "error";

export interface EntityNode {
  opcNode: OPCNode;
  entity: any | null;
  entityId: string;
  entityType: string | null;
  initState: FeatureInitState;
  initError: string | null;
  parentComponentNodeEntityId: string | null;
  parentComponentNode: ComponentNode | null;
  features: FeatureNode[];
}

export interface FeatureNode extends EntityNode {
  parentFeatureNodeEntityId: string | null;
  parentFeatureNode: FeatureNode | null;
}

export interface ComponentNode extends EntityNode {
  children: ComponentNode[];
}

export interface VariableModifier {
  modifierType: string;
  modifierContent: any;
}
