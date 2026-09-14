import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5180,
    // Docker Desktop(Windows)에서 바인드 마운트된 소스는 inotify 이벤트가 전달되지 않아
    // 기본 파일 감시가 변경을 못 잡는 경우가 있다 — 폴링으로 강제한다.
    watch: {
      usePolling: true,
    },
  },
})
