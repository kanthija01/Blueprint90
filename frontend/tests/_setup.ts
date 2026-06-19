// Shared module-resolution shim. Maps native-only modules to in-memory
// JS stubs so we can exercise our stores/lib in plain Node test files.
//
// Usage: import "./_setup" at the TOP of any test that pulls
//   `stores/assessment.ts` or `stores/auth.ts` (which transitively touch
//   AsyncStorage / SecureStore / expo-secure-store).

import Module from "node:module";

type ResolveFn = (request: string, ...rest: unknown[]) => string;

const m = Module as unknown as { _resolveFilename: ResolveFn };
const original = m._resolveFilename;

m._resolveFilename = function (request: string, ...rest: unknown[]) {
  if (request === "@react-native-async-storage/async-storage") {
    return require.resolve("./_stubs/async-storage.js");
  }
  if (request === "expo-secure-store") {
    return require.resolve("./_stubs/secure-store.js");
  }
  return original.apply(this, [request, ...rest] as Parameters<ResolveFn>);
};
