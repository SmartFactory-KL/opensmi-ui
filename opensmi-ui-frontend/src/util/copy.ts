export function createDeepCopy<T>(obj: T): T {
  if (typeof globalThis.structuredClone === "function") {
    return structuredClone(obj);
  } else {
    return JSON.parse(JSON.stringify(obj));
  }
}
