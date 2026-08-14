import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite's config for the DataBound AI frontend.
//
// server.host = true (0.0.0.0) is required so the dev server is reachable
// from outside its Docker container. Without it, Vite only binds to
// localhost inside the container and the host machine can't connect.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
  },
});
