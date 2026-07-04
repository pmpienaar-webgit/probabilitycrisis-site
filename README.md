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
