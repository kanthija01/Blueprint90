// metro.config.js

const { getDefaultConfig } = require("expo/metro-config");
const path = require("path");
const { FileStore } = require("metro-cache");

const config = getDefaultConfig(__dirname);

// Use a stable on-disk cache
const root =
  process.env.METRO_CACHE_ROOT || path.join(__dirname, ".metro-cache");

config.cacheStores = [
  new FileStore({
    root: path.join(root, "cache"),
  }),
];

// Reduce worker count to lower resource usage
config.maxWorkers = 2;

module.exports = config;