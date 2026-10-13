export type RemoteVariableValueType =
  | "Enum"
  | "FloatRange"
  | "Boolean"
  | "ImageJPG"
  | "ImageBMP"
  | "ImagePNG"
  | "ImageGIF"
  | "Text";

export type FeatureEntityType =
  | "RemoteLock"
  | "Attributes"
  | "Identification"
  | "Monitoring"
  | "ParameterSet"
  | "FeatureSetEntity";

export interface FeatureEntityDto {
  entityId: string;
  entityType: FeatureEntityType;
  data: any;
  features: FeatureEntityDto[];
}

export interface ComponentEntityDto extends FeatureEntityDto {
  children: ComponentEntityDto[];
}

export interface VariantValueDto {
  variantType: string;
  value: any;
  dimensions: null | number[];
}

export interface SimpleDataValueDto {
  value: VariantValueDto;
  statusCode: number;
  timestamp: number;
}

export interface RemoteVariableDto {
  name: string;
  nodeId: string;
  entityId: string;
  dataContent: SimpleDataValueDto;
  remoteVariableType: RemoteVariableValueType;
  remoteVariableAnnotation: any;
  tempDataContent?: any;
  timestamp?: string | null;
  isWritable: boolean;
  unit?: string | null;
  children: RemoteVariableDto[];
}

export interface SkillDto {
  name: string;
  nodeId: string;
  entityId: string;
  type: string;
  currentState?: string | null;
  parameterSet: RemoteVariableDto[];
  monitoring: RemoteVariableDto[];
  finalResultData: RemoteVariableDto[];
  dependsOn: string[];
  dependencyOf: string[];
  isSuspendable: boolean;
  minAccessLevel: string;
  parentNodeIdList: string[];
}

export interface MethodDto {
  name: string;
  nodeId: string;
  entityId: string;
  type: string;
  parameterSet: RemoteVariableDto[];
  monitoring: RemoteVariableDto[];
  finalResultData: RemoteVariableDto[];
  minAccessLevel: string;
  parentNodeIdList: string[];
}

export interface ComponentDto {
  name: string;
  nodeId: string;
  entityId: string;
  type: string;
  currentState?: string | null;
  skillSet: SkillDto[];
  methods: MethodDto[];
  monitoring: RemoteVariableDto[];
  attributes: RemoteVariableDto[];
  parameterSet: RemoteVariableDto[];
  components: ComponentDto[];
  parentNodeIdList: string[];
}

export interface LockingModuleDto {
  isEnabled: boolean;
  isSimulated: boolean;
  isLocked: boolean;
  isLockedSince: string;
  lockingUser: string;
  lockingClient: string;
  isLockPending: boolean;
}

export interface MachineDto extends ComponentDto {
  lockingModule: LockingModuleDto;
}
