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

export interface OPCNodeData {
  nodeId: NodeIdData;
  nodeClass: string;
  browseName: QualifiedNameData;
  displayName: LocalizedTextData;
}

export interface FeatureNodeData {
  opcNode: OPCNodeData;

  entity: any | null;
  entityType: string | null;

  children: FeatureNodeData[];
}

export interface ComponentNodeData {
  opcNode: OPCNodeData;

  entity: any | null;
  entityType: string | null;

  features: FeatureNodeData[];

  children: ComponentNodeData[];
}
