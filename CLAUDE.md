# CLAUDE.md

This file is optimized to keep context small.

## What this repo is
Static website and generated notice pages for Polaris-related publishing.

## Token usage rules
- Read only the page being changed (`index.html`, `investment_notices.html`, `work_notices.html`, or `run_all.py`).
- Avoid loading entire HTML files unless the change spans multiple sections.
- Prefer targeted edits over broad formatting.

## Start here by task
- Landing page: `index.html`
- Notice pages: `investment_notices.html`, `work_notices.html`
- Update script: `run_all.py`
- Deployment/setup notes: `RASPBERRY_PI_SETUP.md`

## Preferred workflow
1. Identify the exact page or script.
2. Read only the affected section.
3. Patch minimally.
4. Verify rendered output or generated artifacts.

## Avoid
- Reformatting entire HTML files for small changes.
- Mixing content updates and deployment changes in one patch.
