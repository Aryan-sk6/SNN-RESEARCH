#!/usr/bin/env bash
# Build paper.pdf and summary.pdf from their .md sources (needs pandoc and Playwright with Chromium).
set -euo pipefail
cd "$(dirname "$0")"
for name in paper summary; do
pandoc $name.md -s --embed-resources --css style.css --resource-path=.:.. -o $name.html
NAME=$name node -e "
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/' + process.env.NAME + '.html', { waitUntil: 'networkidle' });
  await p.pdf({ path: process.env.NAME + '.pdf', format: 'A4', printBackground: true });
  await b.close();
})();"
done
