# codex-hive.com v2 parity and link audit (Nov 19, 2026)

Done locally in `/workspace/codex-hive-site-v2`. No push, DNS or GoDaddy edits, and the approved hero was not touched. Backups: `tools/build_v2.py.bak-nov19f`, `backup/docs-nov19f.tgz` and `backup/live-snapshot-nov19f-before.tgz`.

Tools: `tools/crawl_live.py` (fresh crawl, one GET per URL, no redirect following), `tools/render_live.py` (blog bodies are client-rendered on GoDaddy), `tools/parity_check.py` and `tools/link_check.py`. Raw results: `live-snapshot-nov19f/crawl.json`, `audit/parity.json` and `audit/links.json`.

## 1. Live page list (fresh crawl, ~10:05 EST)

Sources: `sitemap.xml` → `sitemap.website.xml`, `sitemap.blog.xml`, `sitemap.ols.xml` and `sitemap.ola.xml`; the home nav, its dropdowns and the "More" menu; the footer (which has no links on live); and a BFS over every same-host link. No same-host link outside the sitemap turned up. A page counts as live only if it returns 200 with no redirect.

- Live nav hrefs: `/`, `/apps-1`, `/blog`, `/contact`, `/correction-notice`, `/daphnis-wake`, `/fractalfs`, `/ftf`, `/interactive`, `/lsfm-vs-hl-3`, `/m/account`, `/music`, `/podcasts`, `/technology-stack-draft`, `/ufft`, `https://newz.codex-hive.com/`, `https://www.facebook.com/100265876391121`, `https://www.linkedin.com/in/valentin-voineag-0b39942a/`, `https://www.x.com/voineag40013`
- `/blog/f/skyborne-three-weeks-of-flight` returned 429 (rate limit) on the first pass and 200 on a single refetch 20 s later.

**Live public pages: 27. v2 pages: 27 (1:1).**

| Live page | Live status | In v2 | Text match | Embeds live/v2 | Live images missing in v2 | Live CTA/links missing in v2 |
|---|---|---|---|---|---|---|
| `/` | 200 | yes | 0.736 | 1/1 | — | — |
| `/apps-1` | 200 | yes | 1.0 | 2/2 | — | — |
| `/blog` | 200 | yes | 0.229 | 0/0 | — | — |
| `/blog/f/a-correction-from-the-hive` | 200 | yes | 0.99 | 0/0 | — | — |
| `/blog/f/daphnis-wake-how-a-tiny-moon-carves-ripples-in-saturns-rings` | 200 | yes | 0.993 | 0/0 | — | — |
| `/blog/f/four-divisions-one-hive-whats-taking-shape-at-codex-hive-labs` | 200 | yes | 0.992 | 0/0 | — | — |
| `/blog/f/heroes-help-rescues-and-chases` | 200 | yes | 0.986 | 0/0 | — | — |
| `/blog/f/join-the-hive` | 200 | yes | 0.988 | 0/0 | — | — |
| `/blog/f/landing-in-new-york` | 200 | yes | 0.986 | 0/0 | — | — |
| `/blog/f/meet-the-divisions-of-codex-hive-labs` | 200 | yes | 0.993 | 0/0 | — | — |
| `/blog/f/meet-the-hive-that-runs-itself-🐝` | 200 | yes | 0.985 | 0/0 | — | — |
| `/blog/f/skyborne-three-weeks-of-flight` | 200 | yes | 0.988 | 0/0 | — | — |
| `/blog/f/the-world-gets-big` | 200 | yes | 0.986 | 0/0 | — | — |
| `/contact` | 200 | yes | 0.674 | 0/0 | — | https://policies.google.com/privacy, https://policies.google.com/terms, tel:2693503043 |
| `/correction-notice` | 200 | yes | 1.0 | 0/0 | — | — |
| `/daphnis-wake` | 200 | yes | 1.0 | 1/1 | — | — |
| `/fractalfs` | 200 | yes | 1.0 | 1/1 | — | — |
| `/ftf` | 200 | yes | 1.0 | 0/0 | — | — |
| `/interactive` | 200 | yes | 1.0 | 3/3 | — | — |
| `/intro` | 200 | yes | 1.0 | 1/1 | — | — |
| `/lsfm-vs-hl-3` | 200 | yes | 1.0 | 0/0 | — | — |
| `/music` | 200 | yes | 1.0 | 1/1 | — | — |
| `/podcasts` | 200 | yes | 1.0 | 1/1 | — | — |
| `/research` | 200 | yes | 1.0 | 1/1 | — | — |
| `/rules-for-use` | 200 | yes | 1.0 | 1/1 | — | — |
| `/technology-stack-draft` | 200 | yes | 1.0 | 1/1 | — | — |
| `/ufft` | 200 | yes | 1.0 | 0/0 | — | — |

Notes on the rows below 1.0 (all expected, nothing missing):
- `/` (0.74): v2 adds the approved static hero (logo, globe video, Join the Hive, "Choose your division →"). Every live word is present in v2, so the missing-word count is 0. The live divisions block is an iframe; v2 has it inline from the approved `divisions-embed.html`.
- `/blog` (0.23): the live server HTML has no post list (GoDaddy renders it client-side), while v2 lists the posts statically. Against the rendered live blog, all 10 post titles are present and "The Codex Frontier" plus the subscribe line match. The live email sign-up form isn't reproduced (see the MIGRATION-STATUS limits).
- `/contact` (0.67): deliberate, per the earlier instruction to show email and phone only. The GoDaddy form, its reCAPTCHA notice with Google Privacy/Terms links, the "please use the form" text and the "Investment inquiries…" line are removed. Live's `tel:2693503043` is `tel:+12693503043` in v2 (same number).
- Blog posts (0.985–0.993): only the GoDaddy "All Posts"/share chrome differs. Bodies, links and images match.
- **Embed text** is identical to live for every page that has an embed: apps-1, daphnis-wake, fractalfs, interactive, intro, music, podcasts, research, rules-for-use and technology-stack-draft.
- **Fresh vs this morning's snapshot:** the only content change on live today is the home divisions embed. Live home now has the clickable Academy **PREVIEW** card linking to `https://academy.codex-hive.com/`. Its content is identical to `/workspace/academy-preview/divisions-embed.html` apart from GoDaddy's iframe wrapper. All 10 blog bodies are unchanged.

## 2. Added or removed in this pass
- **Added:** nothing. No live content was missing from v2. `live-snapshot/` was refreshed from the fresh crawl, and the rebuild only changed `docs/embeds/home_0.html`. That's an unused copy of the live home iframe; v2 uses the inline divisions block. Every other file is byte-identical to `backup/docs-nov19f.tgz`, hero included.
- **Removed:** nothing new. Every v2 page is public on live.

## 3. Hidden and private content check
Fresh status of the private and old URLs on live (one GET each, no redirect following):

```

302 https://codex-hive.com/m/login?r=%2F%25CE%25BB-%25E2%2589%2588-e /%CE%BB-%E2%89%88-e
302 https://codex-hive.com/m/login?r=%2Finfo /info
302 https://codex-hive.com/m/login?r=%2Flive-demo /live-demo
302 https://codex-hive.com/m/login?r=%2Fhive-babble /hive-babble
302 https://codex-hive.com/m/login?r=%2Fblank /blank
302 https://codex-hive.com/m/login?r=%2Foverview /overview
404  /games
301 https://codex-hive.com/technology-stack-draft /architecture-2
404  /architecture
301 https://codex-hive.com/apps-1 /apps
404  /home
404  /papers
404  /newz
404  /hive-buzz
404  /blog/f/why-im-building-in-public-the-lambda-discovery-and-what-comes-n
404  /combos-info
```

- None of Blank, Overview, λ≈e, CombOS Info (`/info`), CombOS Live Demo (`/live-demo`), `/hive-babble` or the deleted "Why I'm Building in Public" post exist in v2. A grep of `docs/` finds 0 links to those paths. The λ≈e PDF was pruned earlier.
- Every v2 nav item is public on live (200): Home, Blog, Music, Podcasts, Newz (`https://newz.codex-hive.com/`), APPS (`/apps-1`), Interactive, UFFT, FTF, LSFM vs HL-3, Technology stack (draft) (`/technology-stack-draft`), FractalFS, Correction Notice, Daphnis Wake and Contact. `/intro` and `/rules-for-use` are 200 on live and, as on live, aren't in the nav.
- **v2 redirect stubs** (noindex; they all point to live public pages): `/architecture-2` → `/technology-stack-draft` (live 301), `/apps` → `/apps-1` (live 301), and `/games` → `/interactive`. These are also stubs in v2 but 404 on live: `/architecture`, `/home`, `/papers`, `/blog/f`, `/newz`, `/hive-buzz` and `/m/*` (→ `/`). They're harmless, but can be dropped if exact 404 parity is wanted.
- The **Academy PREVIEW card** on v2 home comes from the approved embed, and **live home has it now** with the same content.

## 4. Link check (v2 served locally from `docs/`)

**Internal:** 102 unique internal URLs, covering pages, stubs, embeds, assets, srcset files, the video, poster, CSS and the redirect targets. **Broken: 0.**

**External:** every unique external URL in v2, fetched with GET, a browser user agent and redirects followed. The set is identical to live's external links. The only additions are the GA tag and Newz, which live also has, in its nav and in its script.

| URL | Status | Final URL | Result | Used on (v2) |
|---|---|---|---|---|
| https://academy.codex-hive.com/ | 200 | https://academy.codex-hive.com/ | ok | /embeds/home_0.html, /index.html |
| https://astra.codex-hive.com | 200 | https://astra.codex-hive.com/ | ok | /embeds/apps-1_0.html |
| https://babble.codex-hive.com | 200 | https://babble.codex-hive.com/ | ok | /embeds/apps-1_0.html |
| https://doi.org/10.5281/zenodo.17330357 | 200 | https://zenodo.org/records/23887733 | ok | /ufft/index.html |
| https://doi.org/10.5281/zenodo.17438281 | 200 | https://zenodo.org/records/23887624 | ok | /ftf/index.html |
| https://newz.codex-hive.com/ | 200 | https://newz.codex-hive.com/ | ok | /404.html, /apps-1/index.html, /blog/f/a-correction-from-the-hive/index.html |
| https://scribe.codex-hive.com | 200 | https://scribe.codex-hive.com/ | ok | /embeds/apps-1_0.html, /interactive/index.html |
| https://soundcloud.com/valentin-voineag-386211349 | 200 | https://soundcloud.com/valentin-voineag-386211349 | ok | /embeds/music_0.html |
| https://suno.com/@theartificialpulse | 200 | https://suno.com/@theartificialpulse | ok | /embeds/music_0.html |
| https://suno.com/embed/042f3784-58bf-4fd0-91c8-5f6d4fca343a | 200 | https://suno.com/embed/042f3784-58bf-4fd0-91c8-5f6d4fca343a | ok | /embeds/music_0.html |
| https://suno.com/embed/0d0e0c85-4f1d-4af6-a4c0-a4f600019b50 | 200 | https://suno.com/embed/0d0e0c85-4f1d-4af6-a4c0-a4f600019b50 | ok | /embeds/music_0.html |
| https://suno.com/embed/1157e2f0-5de0-47c3-b42a-9e15391fb9a3 | 200 | https://suno.com/embed/1157e2f0-5de0-47c3-b42a-9e15391fb9a3 | ok | /embeds/music_0.html |
| https://suno.com/embed/3d2733d9-92c5-44b8-900d-d52a9dbad387 | 200 | https://suno.com/embed/3d2733d9-92c5-44b8-900d-d52a9dbad387 | ok | /embeds/music_0.html |
| https://suno.com/embed/8f192d17-cfe4-4fee-be60-c1c1e9204b2c | 200 | https://suno.com/embed/8f192d17-cfe4-4fee-be60-c1c1e9204b2c | ok | /embeds/music_0.html |
| https://www.facebook.com/100265876391121 | 400 | https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F100265876391121 | could not verify (Facebook login wall for bots; same URL as live) | /404.html, /apps-1/index.html, /blog/f/a-correction-from-the-hive/index.html |
| https://www.googletagmanager.com/gtag/js?id=G-DW4D6JPPB4 | 200 | https://www.googletagmanager.com/gtag/js?id=G-DW4D6JPPB4 | ok | /404.html, /apps-1/index.html, /blog/f/a-correction-from-the-hive/index.html |
| https://www.linkedin.com/in/valentin-voineag-0b39942a/ | 999 | https://www.linkedin.com/in/valentin-voineag-0b39942a | could not verify (bot block) | /404.html, /apps-1/index.html, /blog/f/a-correction-from-the-hive/index.html |
| https://www.patreon.com/Codex_Hive_Labs/posts/combos-sneak-at-173578011 | 403 | https://www.patreon.com/Codex_Hive_Labs/posts/combos-sneak-at-173578011 | could not verify (members-only post; same URL as live) | /blog/f/meet-the-hive-that-runs-itself-🐝/index.html |
| https://www.patreon.com/c/Codex_Hive_Labs | 200 | https://www.patreon.com/cw/Codex_Hive_Labs | ok | /blog/f/daphnis-wake-how-a-tiny-moon-carves-ripples-in-saturns-rings/index.html, /blog/f/four-divisions-one-hive-whats-taking-shape-at-codex-hive-labs/index.html, /embeds/apps-1_1.html |
| https://www.patreon.com/c/Codex_Hive_Labs. | 200 | https://www.patreon.com/cw/Codex_Hive_Labs | ok | /blog/f/meet-the-divisions-of-codex-hive-labs/index.html |
| https://www.patreon.com/collection/2462507 | 200 | https://www.patreon.com/collection/2462507 | ok | /embeds/apps-1_0.html, /embeds/interactive_0.html |
| https://www.patreon.com/collection/2462508 | 200 | https://www.patreon.com/collection/2462508 | ok | /embeds/research_0.html |
| https://www.x.com/voineag40013 | 200 | https://x.com/voineag40013 | ok | /404.html, /apps-1/index.html, /blog/f/a-correction-from-the-hive/index.html |

Specific checks:
- newz, babble, astra, scribe and academy.codex-hive.com all return 200.
- The /apps-1 cards point to Scribe, Babble, Astra and the Patreon collection, the same targets as live.
- The Academy PREVIEW card links to `https://academy.codex-hive.com/` (200).
- Patreon `c/Codex_Hive_Labs` → `cw/Codex_Hive_Labs` (200). The collections return 200.
- All 5 Suno embeds and suno.com/@theartificialpulse return 200. SoundCloud returns 200.
- X returns 200. LinkedIn returns 999 and Facebook a login redirect, both normal bot blocks, so they count as "could not verify". Patreon post `combos-sneak-at-173578011` returns 403, a members-only post, also "could not verify".
- Both Zenodo DOIs resolve (200). No Spotify or YouTube embeds exist on live or in v2.
- `https://www.patreon.com/c/Codex_Hive_Labs.` (with a trailing dot) is live's own link in a blog post. It still resolves (200), and was left matching live.

**External links failing: none.** Unverifiable because of bot blocks: LinkedIn, Facebook and one members-only Patreon post.

## 5. Content rules
- **Phone:** only (269) 350-3043 appears: 30 text occurrences, all `tel:+12693503043`. the old personal number appears 0 times. ✔
- **"submitted":** the only use is "The χ–H98 fusion manuscript is in preparation and hasn't been submitted yet" in the Oct 15 post, which is negated and matches live. No paper is called submitted. ✔
- **Rosetta Logos:** 0 mentions anywhere in v2 (or in live's public pages). Nothing to flag. ✔
- **"pastor" / "studio":** 0 occurrences. The founder bio says "minister". ✔
- **CombOS:** no performance or benchmark numbers anywhere. These capability statements are verbatim from live and are flagged for Valentin's review:
  - (a) /technology-stack-draft embed: "CombOS is a decentralized operating system designed to self-heal, reconfigure, and scale across distributed nodes". This is design intent, on a page labeled a draft.
  - (b) "Meet the Hive That Runs Itself 🐝" (and its meta/OG description): "CombOS is our swarm operating system project, and it's now running as an interactive demo" and "built on rules and values taken from our real CombOS kernel code". The demo page (`/live-demo`) is Private on live, and v2 doesn't link to it.
  - (c) "Meet the divisions of Codex Hive Labs": "first look at CombOS running as a self-healing swarm".
  None of these is a quantitative performance claim, so all were left matching live. ⚠ (review)


## Follow-up (Nov 19, 10:15 ET): CombOS lines softened
Valentin approved this (relayed by Webster, 10:14 ET). The change is in `tools/build_v2.py` `TEXT_OVERRIDES` and applies to the post body, meta description and og:description. v2 has no RSS/Atom feed, the blog index cards have no excerpts, and the sitemap has no descriptions, so nothing else needed changing. v2 now intentionally differs from live in these lines:
- "Meet the Hive That Runs Itself": "…and it's now running as an interactive demo." → "…and it's still in development. Here's the idea behind it."
- Same post: "It's built on rules and values taken from our real CombOS kernel code." → "Its rules and values follow the CombOS design, which is still in development."
- "Meet the divisions": "…first look at CombOS running as a self-healing swarm" → "…first look at the self-healing swarm design behind CombOS".
- The tech-stack draft's "designed to self-heal" line is unchanged, as instructed. No links to the private live-demo page existed.
- A case-insensitive grep of `docs/` for "now running", "running as a self-healing", "real CombOS kernel" and "interactive demo" finds 0 hits. Internal link check: 102 URLs, 0 broken. The consent test passes.
