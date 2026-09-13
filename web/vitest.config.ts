import { defineConfig } from "vitest/config";
import path from "node:path";

// Minimal config — resolves the @/* path alias to match tsconfig.json's
// existing paths config ({ "@/*": ["./*"] }, relative to web/). No global
// setup file or Redis/network mocking is configured HERE — that was true
// of every test file until session/undo/route.test.ts (this session), which
// mocks @upstash/redis and @/lib/engine-client per-file via vi.mock(),
// scoped to that one file rather than added as shared config. Still no
// vitest-level setup needed for that; noted here so this comment doesn't
// keep claiming no test in this suite ever mocks anything.
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
