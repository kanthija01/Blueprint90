// Minimal in-memory shim so the auth store can be imported in Node tests.
const store = new Map();
module.exports = {
  getItemAsync: async (k) => (store.has(k) ? store.get(k) : null),
  setItemAsync: async (k, v) => { store.set(k, v); },
  deleteItemAsync: async (k) => { store.delete(k); },
};
