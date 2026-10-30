// Shapes of the encoded OPC UA values (see the Python *Data models).
// Swap these for the types in "@/types/OPCTypes" if they already exist there.

import type { NodeIdData } from "@/types/OPCTypes";

/** asyncua can report TwoByte/FourByte for numeric ids, treat them like Numeric. */
export const NUMERIC_NODE_ID_TYPES = ["Numeric", "TwoByte", "FourByte"];

export function defaultNodeId(): NodeIdData {
  return { identifier: 0, namespaceIndex: 0, identifierType: "Numeric" };
}

/** Value for a new array element of the given VariantType. */
export function defaultScalar(type: string): unknown {
  switch (type) {
    case "Boolean":
      return false;
    case "SByte":
    case "Byte":
    case "Int16":
    case "UInt16":
    case "Int32":
    case "UInt32":
    case "Float":
    case "Double":
      return 0;
    case "Int64":
    case "UInt64":
      return "0"; // big ints are strings on the wire
    case "String":
    case "XmlElement":
    case "ByteString":
      return "";
    case "DateTime":
      return new Date().toISOString();
    case "Guid":
      return "00000000-0000-0000-0000-000000000000";
    case "NodeId":
      return defaultNodeId();
    case "ExpandedNodeId":
      return { nodeId: defaultNodeId(), namespaceUri: null, serverIndex: 0 };
    case "QualifiedName":
      return { name: "", namespaceIndex: 0 };
    case "LocalizedText":
      return { text: "", locale: null };
    case "StatusCode":
      return { code: 0, name: "Good", severity: "good" };
    default:
      return null;
  }
}
