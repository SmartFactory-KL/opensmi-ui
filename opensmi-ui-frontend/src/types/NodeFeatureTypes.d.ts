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

export interface OPCNode {
  nodeId: NodeIdData;
  nodeClass: string;
  browseName: QualifiedNameData;
  displayName: LocalizedTextData;
  typeDefinitionId: string | null;
  referenceTypeId: string | null;
  attributes: { [key: string]: string };
  properties: { [key: string]: string };
}

export interface FeatureNode {
  opcNode: OPCNode;

  entity: any | null;
  entityId: string;
  entityType: string | null;

  features: FeatureNode[];
}

export interface ComponentNode {
  opcNode: OPCNode;

  entity: any | null;
  entityId: string;
  entityType: string | null;

  features: FeatureNode[];

  children: ComponentNode[];
}
