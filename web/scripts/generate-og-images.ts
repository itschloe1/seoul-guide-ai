/**
 * generate-og-images.ts
 *
 * Generates Open Graph images (1200x630 PNG) for every guide page
 * and a default image for the homepage.
 *
 * Uses sharp to render SVG -> PNG. No external font files needed;
 * sharp's built-in SVG renderer handles system fonts.
 *
 * Usage:  npx tsx scripts/generate-og-images.ts
 */

import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { GUIDE_META, type GuideMeta } from './guide-meta.js';

// ─── Constants ──────────────────────────────────────────────────────
const WIDTH = 1200;
const HEIGHT = 630;
const OUTPUT_DIR = path.resolve(import.meta.dirname, '..', 'public', 'og');

const KOREAN_BLUE = '#003478';
const WHITE = '#ffffff';
const LIGHT_GRAY = '#f0f4f8';
const TEXT_DARK = '#1a1a2e';
const TEXT_LIGHT = '#6b7280';
const BRAND_NAME = 'Living in Korea';
const SITE_URL = 'www.livinginkorea.co';

// ─── SVG Helpers ────────────────────────────────────────────────────

/** Escape XML special characters */
function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Word-wrap text to fit within a max character width.
 * Returns an array of lines.
 */
function wordWrap(text: string, maxChars: number): string[] {
  const words = text.split(' ');
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    if (currentLine.length + word.length + 1 > maxChars) {
      if (currentLine) lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = currentLine ? `${currentLine} ${word}` : word;
    }
  }
  if (currentLine) lines.push(currentLine);
  return lines;
}

/**
 * Build the SVG string for a guide OG image.
 */
function buildGuideSvg(title: string, category: string): string {
  const titleLines = wordWrap(title, 38);
  const titleFontSize = titleLines.length > 2 ? 40 : 48;
  const titleLineHeight = titleFontSize * 1.25;
  const titleStartY = 260;

  const titleTspans = titleLines
    .map(
      (line, i) =>
        `<tspan x="80" dy="${i === 0 ? 0 : titleLineHeight}">${escapeXml(line)}</tspan>`,
    )
    .join('');

  return `<svg width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${WHITE}" />
      <stop offset="100%" stop-color="${LIGHT_GRAY}" />
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#bg)" />

  <!-- Top accent bar (Korean blue) -->
  <rect width="${WIDTH}" height="8" fill="${KOREAN_BLUE}" />

  <!-- Left accent stripe -->
  <rect x="0" y="0" width="6" height="${HEIGHT}" fill="${KOREAN_BLUE}" />

  <!-- Brand name -->
  <text x="80" y="70" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" fill="${KOREAN_BLUE}">
    ${escapeXml(BRAND_NAME)}
  </text>

  <!-- Divider line -->
  <line x1="80" y1="90" x2="400" y2="90" stroke="${KOREAN_BLUE}" stroke-width="2" stroke-opacity="0.3" />

  <!-- Category badge -->
  <rect x="80" y="130" rx="20" ry="20" width="${Math.max(category.length * 12 + 40, 140)}" height="40" fill="${KOREAN_BLUE}" fill-opacity="0.1" />
  <text x="${80 + 20}" y="157" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="600" fill="${KOREAN_BLUE}">
    ${escapeXml(category)}
  </text>

  <!-- Guide title -->
  <text x="80" y="${titleStartY}" font-family="Arial, Helvetica, sans-serif" font-size="${titleFontSize}" font-weight="700" fill="${TEXT_DARK}">
    ${titleTspans}
  </text>

  <!-- Bottom bar -->
  <rect y="${HEIGHT - 70}" width="${WIDTH}" height="70" fill="${KOREAN_BLUE}" />

  <!-- URL in bottom bar -->
  <text x="80" y="${HEIGHT - 30}" font-family="Arial, Helvetica, sans-serif" font-size="20" fill="${WHITE}" fill-opacity="0.9">
    ${escapeXml(SITE_URL)}
  </text>

  <!-- Decorative circle -->
  <circle cx="${WIDTH - 120}" cy="${HEIGHT - 35}" r="18" fill="${WHITE}" fill-opacity="0.15" />
  <circle cx="${WIDTH - 70}" cy="${HEIGHT - 35}" r="10" fill="${WHITE}" fill-opacity="0.1" />
</svg>`;
}

/**
 * Build the SVG string for the default homepage OG image.
 */
function buildDefaultSvg(): string {
  return `<svg width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${KOREAN_BLUE}" />
      <stop offset="100%" stop-color="#001d42" />
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#bg)" />

  <!-- Decorative circles -->
  <circle cx="950" cy="120" r="200" fill="${WHITE}" fill-opacity="0.03" />
  <circle cx="1050" cy="400" r="150" fill="${WHITE}" fill-opacity="0.03" />
  <circle cx="150" cy="500" r="120" fill="${WHITE}" fill-opacity="0.02" />

  <!-- Brand name (large) -->
  <text x="${WIDTH / 2}" y="260" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="72" font-weight="700" fill="${WHITE}">
    Living in Korea
  </text>

  <!-- Tagline -->
  <text x="${WIDTH / 2}" y="330" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="${WHITE}" fill-opacity="0.8">
    Your guide to life in Korea as a foreigner
  </text>

  <!-- Divider -->
  <line x1="${WIDTH / 2 - 60}" y1="370" x2="${WIDTH / 2 + 60}" y2="370" stroke="${WHITE}" stroke-width="2" stroke-opacity="0.4" />

  <!-- URL -->
  <text x="${WIDTH / 2}" y="420" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="22" fill="${WHITE}" fill-opacity="0.6">
    ${escapeXml(SITE_URL)}
  </text>

  <!-- Bottom accent -->
  <rect y="${HEIGHT - 6}" width="${WIDTH}" height="6" fill="${WHITE}" fill-opacity="0.2" />
</svg>`;
}

// ─── Main ───────────────────────────────────────────────────────────

async function generateImage(svgString: string, outputPath: string): Promise<void> {
  const dir = path.dirname(outputPath);
  await mkdir(dir, { recursive: true });
  await sharp(Buffer.from(svgString)).png().toFile(outputPath);
}

async function main(): Promise<void> {
  console.log('Generating OG images...\n');

  // 1) Default image
  const defaultPath = path.join(OUTPUT_DIR, 'default.png');
  await generateImage(buildDefaultSvg(), defaultPath);
  console.log(`  [ok] ${path.relative(process.cwd(), defaultPath)}`);

  // 2) Guide images
  const entries = Object.entries(GUIDE_META) as [string, GuideMeta][];
  for (const [slug, meta] of entries) {
    const outputPath = path.join(OUTPUT_DIR, `${slug}.png`);
    const svg = buildGuideSvg(meta.title, meta.category);
    await generateImage(svg, outputPath);
    console.log(`  [ok] ${path.relative(process.cwd(), outputPath)}`);
  }

  console.log(`\nDone! Generated ${entries.length + 1} OG images in public/og/`);
}

main().catch((err) => {
  console.error('Failed to generate OG images:', err);
  process.exit(1);
});
