export function mergeStoredSettings<T>(defaults: T, stored: unknown): T {
  if (
    typeof defaults !== "object" ||
    defaults === null ||
    Array.isArray(defaults) ||
    typeof stored !== "object" ||
    stored === null ||
    Array.isArray(stored)
  ) {
    return defaults;
  }

  const result = { ...defaults } as T;

  for (const key of Object.keys(defaults)) {
    if (!Object.prototype.hasOwnProperty.call(stored, key)) {
      continue;
    }

    const defaultValue = (defaults as Record<string, unknown>)[key];
    const storedValue = (stored as Record<string, unknown>)[key];

    // Nested object: recursively merge it.
    if (
      typeof defaultValue === "object" &&
      defaultValue !== null &&
      !Array.isArray(defaultValue)
    ) {
      if (
        typeof storedValue === "object" &&
        storedValue !== null &&
        !Array.isArray(storedValue)
      ) {
        (result as Record<string, unknown>)[key] = mergeStoredSettings(
          defaultValue,
          storedValue,
        );
      }

      continue;
    }

    // Primitive/value: only accept matching types.
    if (typeof storedValue === typeof defaultValue) {
      (result as Record<string, unknown>)[key] = storedValue;
    }
  }

  return result;
}
