type RemoteVariableValueType =
  | "Enum"
  | "FloatRange"
  | "Boolean"
  | "ImageJPG"
  | "ImageBMP"
  | "ImagePNG"
  | "ImageGIF"
  | "Text";

type VariantValueDto = {
  variantType: string;
  value: any;
  dimensions: null | number[];
};

type SimpleDataValueDto = {
  value: VariantValueDto;
  statusCode: number;
  timestamp: number;
};

type RemoteVariableDto = {
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
};

type SkillDto = {
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
};

type MethodDto = {
  name: string;
  nodeId: string;
  entityId: string;
  type: string;
  parameterSet: RemoteVariableDto[];
  monitoring: RemoteVariableDto[];
  finalResultData: RemoteVariableDto[];
  minAccessLevel: string;
  parentNodeIdList: string[];
};

type ComponentDto = {
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
};

type LockingModuleDto = {
  isEnabled: boolean;
  isSimulated: boolean;
  isLocked: boolean;
  isLockedSince: string;
  lockingUser: string;
  lockingClient: string;
  isLockPending: boolean;
};

type MachineDto = ComponentDto & {
  lockingModule: LockingModuleDto;
};
