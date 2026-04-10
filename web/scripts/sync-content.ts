/**
 * Prebuild script: syncs context-library markdown files to Astro content collection.
 * Reads from ../context-library/, injects YAML frontmatter from guide-meta.ts,
 * and writes to src/content/guides/.
 *
 * Run: npx tsx scripts/sync-content.ts
 */

import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { globSync } from 'node:fs';
import { GUIDE_META } from './guide-meta.js';

const ROOT = resolve(import.meta.dirname, '..');
const CONTEXT_LIB = resolve(ROOT, '../context-library');
const OUTPUT_DIR = resolve(ROOT, 'src/content/guides');

// Find all markdown files using a simple recursive approach
function findMdFiles(dir: string, base: string = ''): string[] {
  const { readdirSync, statSync } = await_import();
  const entries = readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const rel = base ? `${base}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      files.push(...findMdFiles(resolve(dir, entry.name), rel));
    } else if (entry.name.endsWith('.md')) {
      files.push(rel);
    }
  }
  return files;
}

// We need sync imports
import { readdirSync, statSync } from 'node:fs';
function await_import() { return { readdirSync, statSync }; }

function parseSourceFile(content: string): { title: string; lastUpdated: string; body: string } {
  const lines = content.split('\n');
  let title = '';
  let lastUpdated = '';
  let bodyStartIndex = 0;

  // Parse # Title line
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith('# ')) {
      title = line.slice(2).trim();
      bodyStartIndex = i + 1;
      break;
    }
  }

  // Parse > Last updated: line and optional --- separator
  for (let i = bodyStartIndex; i < Math.min(bodyStartIndex + 5, lines.length); i++) {
    const line = lines[i].trim();
    if (line.startsWith('> Last updated:')) {
      const match = line.match(/Last updated:\s*(\d{4}-\d{2}-\d{2})/);
      if (match) lastUpdated = match[1];
      bodyStartIndex = i + 1;
    } else if (line === '---') {
      bodyStartIndex = i + 1;
    } else if (line === '') {
      // Skip blank lines after title/metadata
      if (i === bodyStartIndex) bodyStartIndex = i + 1;
    }
  }

  // Skip leading blank lines in body
  while (bodyStartIndex < lines.length && lines[bodyStartIndex].trim() === '') {
    bodyStartIndex++;
  }

  const body = lines.slice(bodyStartIndex).join('\n');
  return { title, lastUpdated, body };
}

function buildFrontmatter(id: string, lastUpdated: string): string | null {
  const meta = GUIDE_META[id];
  if (!meta) return null;

  const fm: Record<string, string | number> = {
    title: meta.title,
    description: meta.description,
    category: meta.category,
    categorySlug: meta.categorySlug,
    order: meta.order,
  };
  if (lastUpdated) fm.lastUpdated = lastUpdated;

  const lines = ['---'];
  for (const [key, value] of Object.entries(fm)) {
    if (typeof value === 'number') {
      lines.push(`${key}: ${value}`);
    } else {
      // Escape quotes in YAML strings
      lines.push(`${key}: "${value.replace(/"/g, '\\"')}"`);
    }
  }
  lines.push('---');
  return lines.join('\n');
}

// Main
console.log('Syncing context-library → web/src/content/guides/');

// Clean output directory
if (existsSync(OUTPUT_DIR)) {
  rmSync(OUTPUT_DIR, { recursive: true });
}

const files = findMdFiles(CONTEXT_LIB);
let synced = 0;
let skipped = 0;

for (const file of files) {
  const id = file.replace(/\.md$/, ''); // e.g., "banking/open-account"
  const raw = readFileSync(resolve(CONTEXT_LIB, file), 'utf-8');
  const { title, lastUpdated, body } = parseSourceFile(raw);

  const frontmatter = buildFrontmatter(id, lastUpdated);
  if (!frontmatter) {
    console.warn(`  SKIP: ${id} (no metadata in guide-meta.ts)`);
    skipped++;
    continue;
  }

  const output = `${frontmatter}\n\n${body}`;
  const outPath = resolve(OUTPUT_DIR, file);
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, output, 'utf-8');
  console.log(`  OK: ${id} (${body.split('\n').length} lines)`);
  synced++;
}

console.log(`\nDone: ${synced} synced, ${skipped} skipped.`);
