import { defineConfig } from "vitest/config";
import path from "node:path";

// Minimal config — resolves the @/* path alias to match tsconfig.json's
// existing paths config ({ "@/*": ["./*"] }, relative to web/). No other
// setup: this pass tests pure logic only, no network/Redis mocking.
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
