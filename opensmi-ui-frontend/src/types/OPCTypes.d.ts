// types/OpcUaTypes.ts

/** Big ints (Int64/UInt64) are strings, as they can exceed Number.MAX_SAFE_INTEGER. */
export type BigIntString = string;

/** NaN and ±Infinity can't be expressed in JSON, so they are encoded as strings. */
export type EncodedFloat = number | "NaN" | "Infinity" | "-Infinity";

/** Base64 encoded bytes. */
export type Base64String = string;

/** ISO 8601 timestamp (UTC). */
export type IsoDateTimeString = string;

export interface QualifiedNameData {
  name: string;
  namespaceIndex: number;
}

export interface LocalizedTextData {
  text: string | null;
  locale: string | null;
}

export type NodeIdType =
  | "TwoByte"
  | "FourByte"
  | "Numeric"
  | "String"
  | "Guid"
  | "ByteString";

export interface NodeIdData {
  /** Guid is a string, ByteString is Base64 */
  identifier: string | number;
  namespaceIndex: number;
  identifierType: NodeIdType;
}

export interface ExpandedNodeIdData {
  nodeId: NodeIdData;
  namespaceUri: string | null;
  serverIndex: number;
}

export interface ReferenceData {
  referenceTypeId: NodeIdData;
  isForward: boolean;
  nodeId: NodeIdData;
  browseName: QualifiedNameData;
  displayName: LocalizedTextData;
  nodeClass: string;
  typeDefinition: NodeIdData | null;
}

export type StatusSeverity = "good" | "uncertain" | "bad";

export interface StatusCodeData {
  code: number;
  /** null if the code is unknown to asyncua's lookup table */
  name: string | null;
  severity: StatusSeverity;
}

/**
 * The first four fields are indexes into the string table of the response
 * they came from, not strings.
 */
export interface DiagnosticInfoData {
  symbolicId: number | null;
  namespaceUri: number | null;
  locale: number | null;
  localizedText: number | null;
  additionalInfo: string | null;
  innerStatusCode: StatusCodeData | null;
  innerDiagnosticInfo: DiagnosticInfoData | null;
}

/**
 * A field of a structure. It carries no type tag, so the shape depends on
 * the field's declared type.
 */
export type MemberValue =
  | null
  | boolean
  | number
  | string
  | NodeIdData
  | ExpandedNodeIdData
  | QualifiedNameData
  | LocalizedTextData
  | StatusCodeData
  | VariantData
  | DataValueData
  | DiagnosticInfoData
  | ExtensionObjectData
  | MemberValue[];

/**
 * A structure.
 * - Decoded: `members` is set, keyed by OPC UA field name, `typeId` is the DataType.
 * - Undecoded: `body` is set (Base64), `typeId` is the NodeId of the encoding.
 */
export interface ExtensionObjectData {
  typeName: string | null;
  typeId: NodeIdData | null;
  members: Record<string, MemberValue> | null;
  body: Base64String | null;
}

export interface DataValueData {
  value: VariantData | null;
  status: StatusCodeData | null;
  sourceTimestamp: IsoDateTimeString | null;
  serverTimestamp: IsoDateTimeString | null;
  sourcePicoseconds: number | null;
  serverPicoseconds: number | null;
}

/** Maps the name of a ua.VariantType to the encoded type of one element. */
export interface VariantScalarMap {
  Null: null;
  Boolean: boolean;
  SByte: number;
  Byte: number;
  Int16: number;
  UInt16: number;
  Int32: number;
  UInt32: number;
  Int64: BigIntString;
  UInt64: BigIntString;
  Float: EncodedFloat;
  Double: EncodedFloat;
  String: string;
  DateTime: IsoDateTimeString;
  Guid: string;
  ByteString: Base64String;
  XmlElement: string;
  NodeId: NodeIdData;
  ExpandedNodeId: ExpandedNodeIdData;
  StatusCode: StatusCodeData;
  QualifiedName: QualifiedNameData;
  LocalizedText: LocalizedTextData;
  ExtensionObject: ExtensionObjectData;
  DataValue: DataValueData;
  Variant: VariantData;
  DiagnosticInfo: DiagnosticInfoData;
}

export type VariantTypeName = keyof VariantScalarMap;

/** Multi-dimensional arrays are nested lists, the shape is in `dimensions`. */
export type NestedArray<T> = (T | NestedArray<T>)[];

export type VariantDataOf<K extends VariantTypeName> =
  | {
      type: K;
      isArray: false;
      dimensions: null;
      value: VariantScalarMap[K] | null;
    }
  | {
      type: K;
      isArray: true;
      /** Only set for multi-dimensional arrays */
      dimensions: number[] | null;
      value: NestedArray<VariantScalarMap[K] | null>;
    };

/** A ua.Variant with an explicit type tag, discriminated on `type` and `isArray`. */
export type VariantData = {
  [K in VariantTypeName]: VariantDataOf<K>;
}[VariantTypeName];
