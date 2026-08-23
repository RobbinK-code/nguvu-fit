import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'Nguvu Fit',
        short_name: 'Nguvu Fit',
        description: 'Home workout plans, gym equipment guide, and progress tracking - built for training anywhere.',
        start_url: '/',
        display: 'standalone',
        background_color: '#faf6ef',
        theme_color: '#ff5a36',
        icons: [
          {
            src: 'icon-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'icon-512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: 'icon-512-maskable.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        // Cache the app shell so it opens instantly on repeat visits.
        globPatterns: ['**/*.{js,css,html,svg,png,ico}'],
        navigateFallbackDenylist: [/^\/(auth|profile|plan|exercises|logs|quotes|payments|admin|equipment|metrics)/],
        runtimeCaching: [
          {
            // Today's plan and quote: try the network first (always want
            // fresh data when online), but fall back to the last
            // successful response when offline - matched by path only
            // so this works regardless of which backend host is set via
            // VITE_API_URL.
            urlPattern: ({ url }) => url.pathname === '/plan' || url.pathname === '/quotes/today',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'nguvu-offline-plan',
              networkTimeoutSeconds: 5,
              expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 7 },
            },
          },
        ],
      },
    }),
  ],
})
