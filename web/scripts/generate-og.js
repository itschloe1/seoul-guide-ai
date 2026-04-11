import sharp from 'sharp';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outPath = path.join(__dirname, '..', 'public', 'og-image.png');

// Korean flag-inspired OG image (1200x630)
const svg = `
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="630" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#e8f0fe"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>

  <!-- Top accent bar (Korean flag colors) -->
  <rect x="0" y="0" width="1200" height="6" fill="#C60C30"/>
  <rect x="0" y="6" width="1200" height="6" fill="#003478"/>

  <!-- Taegeuk (Korean flag center) - positioned left -->
  <g transform="translate(200, 315) scale(1.8)">
    <!-- Red (upper) half -->
    <path d="M0 -60 A60 60 0 0 1 0 60 A30 30 0 0 1 0 0 A30 30 0 0 0 0 -60Z" fill="#C60C30"/>
    <!-- Blue (lower) half -->
    <path d="M0 -60 A60 60 0 0 0 0 60 A30 30 0 0 0 0 0 A30 30 0 0 1 0 -60Z" fill="#003478"/>
  </g>

  <!-- Trigram: Geon (건 / heaven) — top-left of taegeuk -->
  <g transform="translate(80, 160) rotate(-45)">
    <rect x="0" y="0" width="50" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="12" width="50" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="24" width="50" height="6" rx="1" fill="#1f2937"/>
  </g>

  <!-- Trigram: Gon (곤 / earth) — bottom-right of taegeuk -->
  <g transform="translate(290, 430) rotate(-45)">
    <rect x="0" y="0" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="28" y="0" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="12" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="28" y="12" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="24" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="28" y="24" width="22" height="6" rx="1" fill="#1f2937"/>
  </g>

  <!-- Trigram: Gam (감 / water) — top-right of taegeuk -->
  <g transform="translate(290, 160) rotate(45)">
    <rect x="0" y="0" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="28" y="0" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="12" width="50" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="24" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="28" y="24" width="22" height="6" rx="1" fill="#1f2937"/>
  </g>

  <!-- Trigram: Ri (리 / fire) — bottom-left of taegeuk -->
  <g transform="translate(80, 430) rotate(45)">
    <rect x="0" y="0" width="50" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="12" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="28" y="12" width="22" height="6" rx="1" fill="#1f2937"/>
    <rect x="0" y="24" width="50" height="6" rx="1" fill="#1f2937"/>
  </g>

  <!-- Title text -->
  <text x="480" y="270" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="64" font-weight="800" fill="#1a56db">Living in Korea</text>

  <!-- Subtitle -->
  <text x="480" y="330" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="400" fill="#6b7280">Your guide to life in Korea</text>

  <!-- Feature tags -->
  <g transform="translate(480, 370)">
    <rect x="0" y="0" width="100" height="36" rx="18" fill="#C60C30" opacity="0.1"/>
    <text x="50" y="24" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="600" fill="#C60C30">Visas</text>

    <rect x="116" y="0" width="110" height="36" rx="18" fill="#003478" opacity="0.1"/>
    <text x="171" y="24" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="600" fill="#003478">Housing</text>

    <rect x="242" y="0" width="120" height="36" rx="18" fill="#C60C30" opacity="0.1"/>
    <text x="302" y="24" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="600" fill="#C60C30">Banking</text>

    <rect x="378" y="0" width="145" height="36" rx="18" fill="#003478" opacity="0.1"/>
    <text x="450" y="24" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="600" fill="#003478">Healthcare</text>

    <rect x="539" y="0" width="140" height="36" rx="18" fill="#C60C30" opacity="0.1"/>
    <text x="609" y="24" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="600" fill="#C60C30">Daily Life</text>
  </g>

  <!-- Bot callout -->
  <text x="480" y="470" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="500" fill="#1a56db">+ AI-powered Telegram bot for instant answers</text>

  <!-- URL -->
  <text x="480" y="540" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="400" fill="#9ca3af">livinginkorea.vercel.app</text>

  <!-- Bottom accent bar -->
  <rect x="0" y="618" width="1200" height="6" fill="#003478"/>
  <rect x="0" y="624" width="1200" height="6" fill="#C60C30"/>
</svg>`;

const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
await sharp(pngBuffer).toFile(outPath);

console.log(`OG image generated: ${outPath}`);
