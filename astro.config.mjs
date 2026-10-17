import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
export default defineConfig({ site: process.env.SITE_URL || undefined, integrations: [react()], devToolbar: { enabled: false } });
