// Entry for make.fun news-image-20261117 (Node 22, standard library only).
// The image is the entry.png beside this file: a one-page newspaper front
// page drawn from the verified news of Tuesday 17 November 2026. The program
// copies it to the grader's output directory, byte for byte, every run.
//
// Run locally: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
