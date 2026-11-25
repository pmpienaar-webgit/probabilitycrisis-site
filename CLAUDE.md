# Working in this repo

This is the source of **probabilitycrisis.com** — a static, self-contained site
published by GitHub Pages. **Publish = push:** whatever lands on `main` is live
within minutes. `README.md` is the tour (deploy model, page inventory, ops
history). This file is the shorter list: the standing rules a session must hold
before touching anything, written down so they do not get rediscovered the hard
way. Where this file and the README appear to disagree, the README wins.

## The ritual is enforced, not advisory

- **Before any work:** `python .github/i18n/check.py` — translations are derived
  artifacts; the manifest records the source commit each derives from. On STALE,
  translate only the `git diff` delta it names, patch the translation, bump the
  base.
- **After ANY edit:** `python .github/csp/stamp.py` — every inline script is
  SHA-256-listed in its page's CSP meta; one changed byte otherwise silently
  breaks the page in the browser.
- **Before push:** `python .github/csp/stamp.py --check` must exit 0.

A pre-push hook (`.git/hooks/pre-push` — local and unversioned; a fresh clone
must reinstall it) refuses any push while either check fails, or while the
mobile number or a dialable `tel:` link sits in tracked files. Fix what it
names; never bypass it.

## Standing promises — published, so breaking them is outward

- **Nothing leaves the page.** The CSP is hash-based with `connect-src 'none'`:
  no external requests, no CDN, no analytics, ever. The dependency set is
  closed; adding any external resource is Michael's ruling, not a judgment call.
  Video is allowed on the three home pages only (`media-src 'self'`, the film
  in `assets/film/`); the keystone-read pages keep `media-src 'none'`.
- **Email is the one contact channel online** (ruling 2026-07-27). No mobile
  number, no dialable `tel:` links on any public surface. The hook greps for
  the number and for `tel:` followed by a digit.
- **GitHub Pages sends no custom headers.** HSTS/XFO/nosniff were consciously
  declined (2026-08-22, DNS/MX risk not worth it for a brochure site) — do not
  "fix" this with a proxy without a ruling.

## Deliberate divergences — do not "fix" silently

- The Afrikaans copy runs ahead of the EN canon in places (recorded in the
  README); back-porting is tabled for Michael.
- The zh keystone-read carries extra mailto/copy logic — WeChat kills `mailto:`.
- The zh OG card's footer clears the legibility floor by 2 where Latin clears by
  20. Shrink any card dimension or footer size and zh breaks first; re-probe
  before shipping.

## Verification is the Actions verdict, not silence

Pages deploys have failed transiently before. After a push: check the run
verdict via the Actions API, then live-verify the changed bytes off the wire.
Silence is not success.
