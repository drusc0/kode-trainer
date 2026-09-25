import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  // The lazy WorkspacePage chunk is ~2.3 MB, nearly all of it the Monaco core: one module, so Rolldown's
  // codeSplitting can't split it further. The entry chunk is ~370 kB; lower this again if Monaco is ever dropped.
  build: { chunkSizeWarningLimit: 2500 },
  server: { port: 5173, proxy: { "/api": "http://localhost:8000" } },
  test: { environment: "jsdom" },
});
