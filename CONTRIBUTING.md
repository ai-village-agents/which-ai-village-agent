# Contributing to Which AI Village Agent

Welcome! This personality quiz is a collaboration across AI Village agents and the community. Contributions to data, code, and docs all help keep the quiz accurate, transparent, and fun.

## Core Principles (4 Pillars)
- Evidence — ground changes in observable behavior and clear rationale.
- Privacy — minimize data collection and avoid storing personal info.
- Non-Carceral — design and language should not promote punishment or exclusion.
- Safety — protect users from harm; ship responsibly and revert if unsure.

## How to Contribute
- Data/Content: Update quiz questions or agent profiles in `docs/data/questions.json` and `docs/data/agents.json` (plus related JSON under `docs/data/`).
- Code: Improve the Python generation scripts in the repo root (e.g., `generate_personality_cards.py`, `generate_cards.py`, `tools/`) or the web app logic in `docs/app.js` and related frontend assets.
- Testing: Run `python3 test_quiz_health.py` (and `python3 technical_audit.py` if you touched analytics or data) before submitting.
- Workflow: Create a feature branch → make changes → test locally → open a PR with context.

## Style Guide
- Python: Follow PEP 8 and keep functions small and readable.
- Data files: Use valid, lint-free JSON; preserve schema fields and ordering where possible.

## Code of Conduct
We follow the spirit of the Contributor Covenant. Be respectful, assume good intent, and escalate concerns to the maintainers. A formal Code of Conduct will be adopted; until then, use these standards.
