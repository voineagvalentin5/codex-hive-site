import json,urllib.parse as up
R='/workspace/codex-hive-site-v2'
crawl=json.load(open(R+'/live-snapshot-nov19f/crawl.json'));par={r['live']:r for r in json.load(open(R+'/audit/parity.json'))}
links=json.load(open(R+'/audit/links.json'))
priv=open(R+'/live-snapshot-nov19f/private-check.txt').read().strip().splitlines()
L=[]
L.append("# codex-hive.com v2 parity and link audit (Nov 19, 2026)\n")
L.append("Done locally in `/workspace/codex-hive-site-v2`. No push, DNS or GoDaddy edits, and the approved hero was not touched. Backups: `tools/build_v2.py.bak-nov19f`, `backup/docs-nov19f.tgz` and `backup/live-snapshot-nov19f-before.tgz`.\n")
L.append("Tools: `tools/crawl_live.py` (fresh crawl, one GET per URL, no redirect following), `tools/render_live.py` (blog bodies are client-rendered on GoDaddy), `tools/parity_check.py` and `tools/link_check.py`. Raw results: `live-snapshot-nov19f/crawl.json`, `audit/parity.json` and `audit/links.json`.\n")
L.append("## 1. Live page list (fresh crawl, ~10:05 EST)\n")
L.append("Sources: `sitemap.xml` → `sitemap.website.xml`, `sitemap.blog.xml`, `sitemap.ols.xml` and `sitemap.ola.xml`; the home nav, its dropdowns and the \"More\" menu; the footer (which has no links on live); and a BFS over every same-host link. No same-host link outside the sitemap turned up. A page counts as live only if it returns 200 with no redirect.\n")
L.append("- Live nav hrefs: "+', '.join('`'+h+'`' for h in crawl['nav_hrefs'] if h!='#')+"\n- `/blog/f/skyborne-three-weeks-of-flight` returned 429 (rate limit) on the first pass and 200 on a single refetch 20 s later.\n")
L.append("**Live public pages: 27. v2 pages: 27 (1:1).**\n")
L.append("| Live page | Live status | In v2 | Text match | Embeds live/v2 | Live images missing in v2 | Live CTA/links missing in v2 |\n|---|---|---|---|---|---|---|")
for u,v in sorted(crawl['pages'].items()):
  if v.get('status')!=200: continue
  p=up.urlparse(u).path.rstrip('/') or '/';r=par.get(p,{})
  miss=', '.join(r.get('links_missing',[])) or '—'
  L.append(f"| `{up.unquote(p)}` | 200 | {'yes' if r.get('v2') else 'NO'} | {r.get('text_ratio')} | {r.get('iframes_live')}/{r.get('iframes_v2')} | {', '.join(r.get('images_missing',[])) or '—'} | {miss} |")
L.append("""
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
""")
L.append('\n'.join(priv)+"\n```\n")
L.append("""- None of Blank, Overview, λ≈e, CombOS Info (`/info`), CombOS Live Demo (`/live-demo`), `/hive-babble` or the deleted "Why I'm Building in Public" post exist in v2. A grep of `docs/` finds 0 links to those paths. The λ≈e PDF was pruned earlier.
- Every v2 nav item is public on live (200): Home, Blog, Music, Podcasts, Newz (`https://newz.codex-hive.com/`), APPS (`/apps-1`), Interactive, UFFT, FTF, LSFM vs HL-3, Technology stack (draft) (`/technology-stack-draft`), FractalFS, Correction Notice, Daphnis Wake and Contact. `/intro` and `/rules-for-use` are 200 on live and, as on live, aren't in the nav.
- **v2 redirect stubs** (noindex; they all point to live public pages): `/architecture-2` → `/technology-stack-draft` (live 301), `/apps` → `/apps-1` (live 301), and `/games` → `/interactive`. These are also stubs in v2 but 404 on live: `/architecture`, `/home`, `/papers`, `/blog/f`, `/newz`, `/hive-buzz` and `/m/*` (→ `/`). They're harmless, but can be dropped if exact 404 parity is wanted.
- The **Academy PREVIEW card** on v2 home comes from the approved embed, and **live home has it now** with the same content.
""")
ib=links['internal_bad']
L.append(f"## 4. Link check (v2 served locally from `docs/`)\n\n**Internal:** {len(links['internal'])} unique internal URLs, covering pages, stubs, embeds, assets, srcset files, the video, poster, CSS and the redirect targets. **Broken: {len(ib)}.**\n")
L.append("**External:** every unique external URL in v2, fetched with GET, a browser user agent and redirects followed. The set is identical to live's external links. The only additions are the GA tag and Newz, which live also has, in its nav and in its script.\n")
L.append("| URL | Status | Final URL | Result | Used on (v2) |\n|---|---|---|---|---|")
for u,c,fin,res,pages in links['external']:
  if 'facebook.com' in u: res='could not verify (Facebook login wall for bots; same URL as live)'
  if 'combos-sneak' in u: res='could not verify (members-only post; same URL as live)'
  L.append(f"| {u} | {c} | {fin} | {res} | {', '.join(pages[:3])} |")
L.append("""
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
""")
open(R+'/PARITY-AUDIT-2026-11-19.md','w').write('\n'.join(L)+'\n');print('written')
