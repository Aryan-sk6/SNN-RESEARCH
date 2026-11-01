#!/usr/bin/env bash
# Build paper.html and paper.pdf from paper.md (needs pandoc and Playwright with Chromium).
set -euo pipefail
cd "$(dirname "$0")"
pandoc paper.md -s --embed-resources --css style.css --resource-path=.:.. -o paper.html
node -e "
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/paper.html', { waitUntil: 'networkidle' });
  await p.pdf({ path: 'paper.pdf', format: 'A4', printBackground: true });
  await b.close();
})();"
