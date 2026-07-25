# probabilitycrisis-site

**The live practice website** — deploys to https://probabilitycrisis.com via GitHub Pages on every push to `main`. Load-bearing repo (root `MAP.md`).

## Operating knowledge
- **Publish = push.** No separate deploy step. Live in ~90s; CDN caches 10 min (hard-refresh to verify).
- **Transient deploy failures are a known GitHub Pages behaviour** (build succeeds, "Deploy to GitHub Pages" step fails — 3 occurrences 2026-07-03/04). Remedy: empty commit to retrigger. Watchers should check the RUN VERDICT via the Actions API, not just poll content — silence is not success.
- **Source of truth chain:** `Prob Crisis\Website\hook-layer-draft\` (site pages) and `Prob Crisis\Website\web-edition-draft\boutique\` (the working paper) are the editable sources; this repo holds deploy copies. Edit source → copy here → push. Keep `Prob Crisis\Website\index*.html` mirrors in sync.
- **PDFs are compiled artifacts** — edit the HTML source, re-render via Chrome headless `--print-to-pdf` (ABSOLUTE paths — relative output paths fail silently), then copy here. `what-i-do.pdf` = the boutique edition (house standard: dark full-bleed cover, cream full-bleed body). `profile.pdf` = the one-pager (30-Second-Gate + Barrage certified).
- **Standing promises this site carries** (audited by the Adversarial Barrage): "the first conversation is free and there's no pitch" (permanent policy) · the Keystone Read's "nothing leaves the page" (zero network calls — re-verify the zero-external-request property on every substantive change).
- **DNS**: zone on Google nameservers; MX = Google Workspace (live email — never touch); A records → GitHub Pages IPs; CNAME file pins the domain.

## Contents
`index.html` (Hybrid cut, the lead) · `index-primary.html` (Primary cut) · `keystone-read.html` (the instrument) · `profile.pdf` · `what-i-do.pdf` · `assets/seal-email.png` (feeds the email-signature seal variant) · `CNAME` · `robots.txt`

## Translations
`index.html` is the canonical English source, forever; `index.zh.html` (Simplified Mandarin) and `index.af.html` (Afrikaans) are derived artifacts, never edited independently of it — the same holds for `keystone-read.zh.html` / `keystone-read.af.html` against `keystone-read.html`. The manifest at `.github/i18n/manifest.json` records the exact source commit each translation derives from. **Run `python .github/i18n/check.py` before any site work** — it flags drift between the source and each translation's recorded base. On STALE: `git diff <base>..HEAD -- index.html`, translate only the delta, patch the translation, then bump `base` in the manifest to the new hash.

Two recorded, deliberate divergences (2026-07-25 — the drift-check cannot see either; do not "fix" them silently):
1. **The af door runs slightly ahead of the English canon**, from Michael's native walk-through: it adds *kleiner besighede* (audience), *in die beplanning* (where-he-works list), *of onsekerheid* (counterparty composite), *en bevestig* (stakeholder lens), *kennis-sintese en samewerking* (AI lens), *op die kruispad tussen besluit en impak* (hero subhead), *Strategiese* (procurement symptom). A back-port of these into `index.html`/`index.zh.html` is tabled as a decision for Michael; until taken, the af wording wins on the af page only.
2. **`keystone-read.zh.html` carries sanctioned extra script logic** in its mailto/toast handler: WeChat's in-app browser kills `mailto:`, so the zh instrument copies the address *and* the composed read together and says so in the toast. Behavioural divergence is intentional there and only there; every other script difference across the six pages is string-table translation only.
