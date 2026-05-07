# Contributing

Telos is opinionated by design. Contributions are welcome — but the bar is "does this make founders ship the right product, or the wrong product faster?"

## What this project is

A Claude Code plugin + brain MCP server that enforces validation discipline before founders write product code. Synthesizes well-established startup-validation methodology into one unified voice.

## What this project is NOT

- A general-purpose Claude Code starter
- A productivity tool
- A neutral framework — it has strong opinions
- A SaaS product

If your contribution makes it more general-purpose or less opinionated, it's probably going in the wrong direction.

## Good contributions

- **Skill prompt improvements** — sharper questions, better refusal wording, more specific reframes of solution-thinking into problem-thinking
- **Bug fixes** in the brain MCP server or hook script
- **New skills** that fit the methodology (e.g., `/pivot`, `/story`, `/pmf-check`, `/dance`) — open an issue first to discuss fit
- **Better tests** — especially edge cases in the hook
- **Quality-of-life** — clearer error messages, better install detection, recovery from common mistakes

## Less-good contributions

- **Generalizing** the framework to non-startup contexts
- **Removing** opinions to make it more flexible
- **Adding** vanity-metric tracking, pretty dashboards, or anything that celebrates output without retention
- **Auto-resolving** the friction the hook creates — the friction is the feature

## Contribution flow

1. Open an issue describing the change before opening a PR. Skill additions especially need design alignment.
2. Run all 4 test suites locally before submitting:
   ```
   python3 tests/test_mcp.py
   bash   tests/test_hook.sh
   python3 tests/test_skills.py
   python3 tests/test_integration.py
   ```
3. Match the existing voice in skill prompts: direct, opinionated, no hedging.
4. PRs that change skill prompts should include the *why* — what failure mode is the new wording protecting against?

## Methodology

If you're adding or modifying skills, ground in the canonical startup-validation discipline:

- **Customer Development** — process spine, "get out of the building," earlyvangelist test
- **Lean Startup** — Build-Measure-Learn, validated learning, pivot-vs-persevere, the 10 pivot types
- **Fall in love with the problem** — believer thesis, founder's anchor, story-led pitch
- **Do things that don't scale** — default-alive math, recruit users one-by-one, schlep blindness
- **Interview discipline** — past behavior over opinions about the future

These ideas are well-documented across decades of founder writing. Telos makes them executable inside the tool we already use to build.

## License

MIT — by contributing you agree your contributions are MIT-licensed.
