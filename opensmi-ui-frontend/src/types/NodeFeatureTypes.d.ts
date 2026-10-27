export interface NodeIdData {
  identifier: string | number;
  namespaceIndex: number;
  identifierType: string;
}

export interface QualifiedNameData {
  name: string;
  namespaceIndex: number;
}

export interface LocalizedTextData {
  text: string | null;
  locale: string | null;
}

export interface ReferenceData {
  referenceTypeId: NodeIdData;
  isForward: boolean;
  nodeId: NodeIdData;
  browseName: QualifiedNameData;
  displayName: LocalizedTextData;
  nodeClass: string;
  typeDefinition: NodeIdData;
}

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
