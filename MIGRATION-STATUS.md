# codex-hive.com static rebuild v2: migration status

Built Nov 19, 2026 from a fresh fetch of the live GoDaddy site (same day). Everything here is local on the box.
No GitHub repo was created and nothing was pushed or deployed. Netlify, DNS and the live GoDaddy site were not touched.
The original `/workspace/codex-hive-site` is unchanged (last modified Nov 16, 20:10 EST).

## Layout
| Path | What it is |
|---|---|
| `docs/` | The publishable site. GitHub Pages: "Deploy from a branch → main → /docs". Includes `CNAME` (codex-hive.com), `.nojekyll`, `404.html`, `robots.txt`, `sitemap.xml` |
| `tools/build_v2.py` | Rebuilds `docs/` from `live-snapshot/` (`docs/style.css` and `docs/assets/` are kept across rebuilds; all other files are regenerated). It writes only inside v2. It's not the old `site/build.py` and doesn't touch the shared `site/out` |
| `tools/render_live.py`, `tools/screenshots.py` | Headless Chrome (system `/usr/bin/google-chrome` via Playwright) for blog rendering and screenshots |
| `live-snapshot/` | The Nov 19 fetch of every live public page (raw HTML), the rendered blog DOM, the sitemaps, the RSS/Atom feeds, and the live home divisions embed |
| `screenshots/` | `{home,apps,contact}-{v2,live}-{1440,390}.png` (full page) |
| `pages.json`, `tools/text-parity.txt`, `tools/pruned-assets.json` | Page list, text match scores vs live, and the old assets that were dropped |

To rebuild: `cd /workspace/codex-hive-site-v2 && python3 tools/build_v2.py`. To refresh from live, first re-fetch `live-snapshot/` (see the commands in the scripts).

## Pages (27 real pages + 14 redirect stubs)
**Included.** These are all the public pages in the live sitemap (`sitemap.website.xml` + `sitemap.blog.xml`):
/, /blog/, /music/, /podcasts/, /apps-1/, /interactive/, /research/, /ufft/, /ftf/, /lsfm-vs-hl-3/, /technology-stack-draft/, /fractalfs/, /correction-notice/, /daphnis-wake/, /contact/, /intro/ and /rules-for-use/ (public but hidden from the nav, same as live), plus 10 blog posts. One of them, *A correction from the Hive* (Nov 5), is new and wasn't in the Nov 3 build.

**Removed from the Nov 3/16 build** (these are Private on live and 302 to /m/login): `/λ-≈-e/`, `/info/`, `/live-demo/`, `/hive-babble/`. `/blank` and `/overview` weren't in the old build and stay out.
Also removed: the blog post *Why I'm Building in Public: The Lambda Discovery…*, because it returns 404 on live now. Netlify-only files (`_redirects`, `netlify.toml`) and the 50 MB `deploy.zip` were left out too.
Unreferenced assets were pruned: the λ≈e paper PDF, the CombOS info image, the Hive-Babble logo, unused hero images, and a duplicate podcast MP3.

**Redirect stubs.** Each one is a small `index.html` with meta refresh, a canonical link, `location.replace` JS and a visible link, and is marked noindex:
| From | To |
|---|---|
| /architecture-2, /architecture | /technology-stack-draft/ (live: 301) |
| /games | /interactive/ (live: 404 today; added on request) |
| /apps | /apps-1/ (live: 301) |
| /home | / |
| /papers | /research/ |
| /blog/f | /blog/ |
| /newz, /hive-buzz | https://newz.codex-hive.com/ |
| /m/login, /m/create, /m/create-account, /m/reset, /m/account | / (membership is gone) |

Old Netlify wildcards (`/m/*`, `/blog/f/*`) can't be done on Pages. Any other unknown path gets `404.html`.

## What matches live (checked Nov 19)
- **Text.** Every page except home and contact scores 1.00 on word-level text match with the live page sections (`tools/text-parity.txt`). Home scores 0.79 because of the static intro and the inlined divisions. Contact scores 0.85 because the form fields are replaced.
- **Titles and meta descriptions** come from live on every page. That includes the new descriptions on apps-1, interactive, ftf, music, fractalfs, technology-stack-draft, daphnis-wake and contact. OG tags come from live; og:url and canonical point to https://codex-hive.com/….
- **HTML embeds** are copied verbatim from live, with images made local and links made site-relative. That covers the © 2026 iframe footers on /intro and /rules-for-use, and the Apps embed with Hive Scribe, Hive-Babble and **Hive Astra (https://astra.codex-hive.com)**.
- **Nov 19 fixes:**
  - The blog subscribe line reads "Subscribe for research notes, game and music updates, and new posts from the Hive."
  - The Oct 15 *Four divisions* post uses Codex Hive Research, Codex Hive Interactive and Codex Hive Publishing (coming soon).
  - The architecture diagram is gone.
  - /interactive has the heading "Codex Hive Interactive".
  - The founder photo alt is "Valentin Voineag", with GoDaddy's crop kept.
  - The Join the Hive image has alt text.
  - Contact has no 24/7 chat line.
  - Technology stack (draft) lives at /technology-stack-draft.
- **Nav** is identical on all 27 pages (one md5) and matches the live nav: Home · Blog · Hive Buzz (Music, Podcasts, Newz → https://newz.codex-hive.com/) · Interactive (APPS, Interactive) · Research (UFFT, FTF, LSFM vs HL-3, Technology stack (draft), FractalFS, Correction Notice, Daphnis Wake) · Contact.
- **Footer** has the live legal text and the phone (269) 350-3043 only. Neither the old number nor `hive-buzz-newz.netlify.app` appears anywhere in `docs/`.
- **Hive Academy PREVIEW card (updated Nov 19).** The current `/workspace/academy-preview/divisions-embed.html` (modified 08:43 EST) is inlined on home. The **whole Academy card is now a link** to https://academy.codex-hive.com/, and all linked cards lift on hover (translateY + gold glow, and reduced-motion is respected). The earlier version is `divisions-embed-v1.html`. As of the 10:05 EST crawl, live home has this same embed (content identical apart from GoDaddy's iframe wrapper), so live and v2 match. The intro hexagon for Academy now says "Preview" instead of "Coming Soon".
- **Internal links:** 0 broken across `docs/`.

## Home hero rework (Nov 19, after the cutover was rejected over the intro logo)
- **Originals backed up** (outside `docs/`, so they aren't published or pruned): `backup/hero-orig/` has the old landing.mp4/.webm/poster and globe images, and `backup/logo-header.png`.
- **Video re-encoded** from the backup with ffmpeg crop **`crop=1280:332:0:226`** (rows 226–557 of 720; full width). The baked tagline ends around y≈205–210 and the baked button glow starts around y≈565. Text and button are in the same place in every frame. I checked all 145 frames, including the first and last, on contact sheets and at full resolution along the top and bottom edges: no baked text, chevrons or button remain.
  - `landing.mp4`: H.264 High, CRF 28, yuv420p, `+faststart`, no audio, 1280×332, 6.04 s, 1.21 MB (was 1.96 MB)
  - `landing.webm`: VP9, CRF 44, no audio, 1.41 MB (was 1.69 MB)
  - `landing-poster.jpg`: frame at 1.5 s of the cropped video, 120 KB
  - The sources carry `?v=20261119` to bust caches.
- **Real logo as HTML** above the globe: `/assets/hero/codex-hive-logo-stacked.svg` (copied from `/workspace/branding/`) via `<picture>`, with a 638 px PNG fallback. It's centered, with `alt="Codex Hive Labs"`, 210 px wide at 1440 and 150 px at 390.
- **HTML "Join the Hive" button** (gold outline) links to https://www.patreon.com/c/Codex_Hive_Labs in a new tab. That's the same URL as live's "Join the Hive on Patreon" CTA. In the old static build, the transparent hotspot over the baked button opened the division picker instead. The picker is now reached from a small "Choose your division →" link under the button; "Choose your division" is the picker's existing title. Tested: the button opens Patreon, and the link opens the hex picker.
- **Layout:** the stage stays 16:9 on desktop. On phones (≤760 px) it's 4:5, so the logo, globe band and button fit. The video band has soft top and bottom fades. No horizontal scroll at 390.
- **Header logo:** checked; no change needed. `docs/assets/logo-header.png` (128×114, shown at 48×43) is the hex C mark with CODEX / HIVE. It matches live's nav logo (`codex-hive-logo-official.png`) and `/workspace/branding/official/codex-hive-logo-official.png`. It's the same on all 27 pages and the 404.
- Note: the stacked SVG in `/workspace/branding/` is a cleaner vector version, with a flatter white/gold finish than the metallic official PNG used in live's header. Same mark, slightly different finish.
- Also fixed: `og:image` is now an absolute URL (`https://codex-hive.com/assets/…`), as Open Graph requires.
- **Other images with the baked "CODEX HIVE LABS" chevron wordmark:** none in v2 `docs/`. I inspected all 45 images visually. Leftovers exist only in the untouched original `/workspace/codex-hive-site/assets/`, and v2 doesn't use any of them:
  - `hero/hero2-fb.png` (+ `hero2.webp`): an old hero mockup with the "CODEX HIVE LABS" wordmark, chevrons, the tagline and an "EXPLORE THE HIVE" button
  - `hero/hero1-fb.png` (+ `hero1.webp`): an old mockup with a small "CODEX HIVE LABS" header wordmark
  - `assets/hero/landing.*` in the original: the old baked video
  - Division logos with their own "Codex Hive" lettering are a different design and were left alone: `326a3522/div_326a3522/e393f072_sq-interactive-logo.png` (CODEX HIVE INTERACTIVE, used on /interactive, home and the Apps embed) and `975b02a3/div_975b02a3_codex-hive-publishing-crest` (home divisions).
- **Screenshots:** `screenshots/home-v2-hero-1440.png`, `screenshots/home-v2-hero-390.png` (first screen), `screenshots/home-v2-1440.png` and `screenshots/home-v2-390.png` (full page), and `screenshots/hero-video-strip.png` (frames 0, 72 and 144 of the new video). Layout shots are taken with the cookie banner dismissed. `home-v2-390-cookie-banner.png` predates the hero change.

## Hero logo v3: official metallic artwork (Nov 19, after Valentin said "sizes not quite there")
- **Source:** `/workspace/branding/codex-hive-logo-official-metallic-ref.png`. It's actually **1254×1254** RGB, not 1024. Nothing was redrawn or re-typeset; the cutout is the reference pixels themselves.
- **Cutout:** made by `tools/logo/cutout.py`. Masters are in `tools/logo/` and `/workspace/branding/`: `codex-hive-logo-metallic-cutout.png` and `.webp` (lossless), **971×865**, tight crop (6 px padding) of the source box x152–1123, y184–1049.
- **How the key works:**
  1. The textured background, including the brighter top-right vignette, is rebuilt as a clean plate by inpainting the logo area and blurring.
  2. Each pixel's brightness above that plate becomes a difference value. Pixels above 45 count as solid. Specks under 150 px are dropped, letter counters stay open, and a 3 px close is applied.
  3. Opacity ramps softly from a difference of 12 to 60 only in a thin band around the solid shapes. Drop shadows are darker than the plate, so they key out.
  4. Edges are cleaned with `(I − (1−a)·B)/a` against the plate, and a final pass removes anything under 150 px.
  5. The result is exactly 16 opaque pieces (C, 4 bars, C-O-D-E, X + orange slash, H-I-V-E) with nothing stray. It was checked on pure black, mid-gray and the hero color (`tools/logo/test-on-*.png`): no gray halo, box or specks.
  The thin darker rims on the letters are the artwork's own bevel, not a halo.
- **Hero sizes** (built by `build_v2.py`, which uses premultiplied Lanczos so edges don't darken, plus a light unsharp):
  - `docs/assets/hero/codex-hive-logo-{170,250,340,500}.{png,webp}`
  - Shown at **250×223 css at 1440** (2x file 500 w), up from 210 px. **170×151 css at 390** (2x file 340 w).
  - Uses `srcset`/`sizes` with WebP plus PNG fallback, and `alt="Codex Hive Labs"`.
  - Checked in headless Chrome: DPR 1 loads 250/170 and DPR 2 loads 500/340.
  - Every size is a downscale of the 971 px master. **Source limit:** about 971 px wide for the whole lockup, so sharp up to about 485 css px at 2x. Going bigger would need upscaling or a higher-res original.
- **Replaced (backed up in `backup/hero-logo-prev/`):** the stacked SVG/PNG hero logo. The "Join the Hive" button (Patreon) and "Choose your division →" link are unchanged.
- **Header logo: no change.** `docs/assets/logo-header.png` (128×114) has the same proportions as the reference cutout: aspect 1.123 vs 1.124, silhouette overlap IoU 0.96, and the gaps between mark, CODEX and HIVE match to about 1% of the height (`tools/logo/header-compare.png`). So it stays as is on every page.
- **Screenshots:** `screenshots/home-v2-hero-1440.png`, `screenshots/home-v2-hero-390.png` and `screenshots/logo-ref-vs-cutout.png` (the reference next to the cutout on the hero background, same scale).

## Parity and link audit (Nov 19, 10:05 EST): see `PARITY-AUDIT-2026-11-19.md`
- Fresh crawl of the live sitemaps, nav, footer and same-host links: **27 public pages on live, 27 in v2 (1:1)**. Nothing was missing, so nothing was added or removed. The private pages (Blank, Overview, λ≈e, /info, /live-demo, /hive-babble) and the deleted "Why I'm Building in Public" post are absent from v2. Every v2 nav item is public on live.
- The only live change since the morning snapshot is the home divisions embed (Academy PREVIEW, now live). `live-snapshot/` was refreshed (the old one is in `backup/live-snapshot-nov19f-before.tgz`). The rebuild was byte-identical to the backup apart from the unused `docs/embeds/home_0.html`, and the hero wasn't touched.
- Link check on v2 served locally: **102 internal URLs, 0 broken**. **23 external URLs, 0 failing.** LinkedIn (999), Facebook (login wall) and one members-only Patreon post (403) couldn't be verified because of bot blocks. The external link set is identical to live's.
- Rules: phone (269) 350-3043 only; no "submitted" paper; no Rosetta Logos mentions; no "pastor" or "studio". There are no CombOS performance numbers. Three verbatim-from-live CombOS capability phrasings were flagged. **Update, 10:15 ET:** with Valentin's approval, v2 softens the two blog-post lines through `TEXT_OVERRIDES` in `build_v2.py` ("still in development" / "follow the CombOS design" / "self-healing swarm design behind CombOS"). The tech-stack draft's "designed to self-heal" is kept. These lines now differ from live on purpose.
- Re-run: `python3 tools/crawl_live.py live-snapshot-nov19f`, then `tools/parity_check.py`, then `tools/link_check.py` (with `docs/` served on :18741), then `tools/write_audit.py`.

## What differs from live, and why
1. **Look and layout.** v2 uses the simple dark static theme from the Nov 3 build. GoDaddy's grid, fonts, button styling and background images aren't reproduced pixel for pixel. Text, order and images match; the visual design is simpler. Compare the screenshots.
2. **Home** keeps the static animated intro (now: official metallic logo cutout + cropped globe video + Join button → division hexes) in place of GoDaddy's hero. The live content follows below it. The divisions block is inline HTML rather than an iframe.
   **About (updated Nov 19)** now matches live's layout. It's two columns, with the honeycomb image left and Our Mission right, then Founder & Lead Researcher left and a round founder photo right. Images are 532×532 at x=164 and x=744 at 1440, the same as live measured in headless Chrome; at 390 they stack full-width at 342 px, also the same as live. Text is centered under gold (#f2a900) headings, with a "Contact the Founder" button. The font is Roboto/system; live's League Spartan headline font isn't loaded.
3. **Header.** There's no GoDaddy "More" overflow menu (the duplicate More is being handled separately) and no account icon. The social links (Facebook, LinkedIn, X) are in the footer instead of the header. Patreon was dropped from the old static footer to match live.
4. **Contact (updated Nov 19).** There's no form. The page shows live's heading, its first intro sentence, Email VoineagValentin@codex-hive.com (the exact address on live Contact), Phone (269) 350-3043, the Hours table exactly as live shows it, and Connect With Us links. The "please use the form" sentence, the "Investment inquiries…" line and the form note were removed. Put a form back once a free option is picked (see below).
5. **Blog.** There's no subscribe form (only the line), no share buttons, no "Recent Posts" sidebar, and no RSS/Atom feed. The posts and dates are the same.
6. **Analytics + cookie banner (updated Nov 19).** The same GA4 tag as live (**G-DW4D6JPPB4**) is in the `<head>` of all 27 pages and `404.html`. It's left off the 14 redirect stubs, because they redirect instantly. **Consent Mode v2:** before `gtag('config')`, the defaults are set to `analytics_storage`, `ad_storage`, `ad_user_data` and `ad_personalization` = `denied`. A stored `granted` (localStorage key `ch_cookie_consent`) is applied with `gtag('consent','update',{analytics_storage:'granted'})` on page load.
   **Banner:** it's self-hosted, with no third-party script, and appears on the same 28 pages. It's a small charcoal and gold card fixed to the bottom right (full width at 480 px and below), using `role="dialog"`, `aria-label="Cookie consent"`, `aria-describedby`, real `<button>`s and a visible focus ring. The wording and single **Accept** button are copied from the live GoDaddy banner: "This website uses cookies." / "We use cookies to analyze website traffic and optimize your website experience. By accepting our use of cookies, your data will be aggregated with all other user data." Live has no privacy-policy link, so none was added. Accept stores `granted`, sends the consent update and hides the banner for good.
   **Decline:** live has no Decline button, so none is shown. Until someone accepts, consent stays denied and the banner keeps appearing. The decline logic (it stores `denied`, keeps consent denied and hides the banner) is already in place. Set `SHOW_DECLINE=True` in `tools/build_v2.py` to show a "Decline" button; that label isn't on live, so it needs Valentin's OK. Note that GDPR-style consent normally expects an equally easy way to refuse.
   **Tested** in headless Chrome at 390 (`tools/test_consent.py`, results in `tools/consent-test.txt`). The banner shows on the first visit, consent defaults to all denied, and the GA hit is sent cookieless (`gcs=G100`). Accept hides it, stores `granted` and pushes the update. After a reload, the banner stays hidden and the stored grant is applied. It doesn't appear on other pages either. Screenshot: `screenshots/home-v2-390-cookie-banner.png`.
7. **Trailing slashes.** GitHub Pages serves `/music/` and 301s `/music` → `/music/`, so old links keep working.

Content note: the retraction text on /correction-notice, /ufft, /ftf and the Nov 5 blog post mentions SPARC and λ ≈ e only as withdrawn or corrected. That's live text, copied unchanged. No new claims were added.

## What the GoDaddy builder does that static can't do as-is (free options)
| Builder feature | On live now | Static status | Free option |
|---|---|---|---|
| Contact form (+ reCAPTCHA) | yes | removed; email and phone shown | Formspree free tier, Web3Forms, or a Google Form link/embed. Or keep email/phone only |
| Blog subscribe / email sign-up | yes | line only | Buttondown or MailerLite free tier embed form, or Patreon follow |
| Blog RSS/Atom (`/blog/f.rss`, `.atom`) | yes | none | Generate a static `feed.xml` in `build_v2.py` (simple to add) |
| Cookie banner | yes (GoDaddy COOKIE_BANNER) | **done**: self-hosted banner with the same wording and Accept button + Consent Mode v2 (denied by default) | Optional: show a Decline button (`SHOW_DECLINE=True`) |
| Google Analytics (G-DW4D6JPPB4) + GoDaddy traffic tag | yes | GA4 gtag **added** (GoDaddy's own traffic tag not carried over) | Add the same gtag snippet (needs banner/consent), or cookieless options like GoatCounter (free for personal use) or Cloudflare Web Analytics (free) |
| Membership / sign-in (`/m/*`), Private pages | yes | none (stubs → home) | Not available on Pages. Private pages stay off the static site |
| Blog CMS / in-browser editing | yes | edit HTML or re-run the build | Edit in GitHub's web editor; optional Decap CMS (free) later |
| Builder SEO/sitemap auto-updates | yes | static `sitemap.xml` + `robots.txt` generated | Regenerate on build |
| Header/footer social icons, share buttons | yes | text links | Cosmetic; can add SVG icons |

## Cutover steps (only after Valentin says yes)
**Before you start:** lower the TTL on the codex-hive.com A and www records at GoDaddy to 600 s a day ahead. Take a fresh `live-snapshot` and rebuild so the content is current. Keep the GoDaddy Website Builder plan active until the new site has been verified for at least a week. Unpublishing is optional and comes last.

1. **Create the repo.** Make a public repo `voineagvalentin5/codex-hive-site` (Pages is free for public repos). Push the contents of `/workspace/codex-hive-site-v2` (`docs/` + `tools/` + this file; `live-snapshot/` and `screenshots/` are optional) to `main`.
2. **Turn on Pages.** Go to Settings → Pages → Source: *Deploy from a branch*, Branch `main`, folder `/docs`. Wait for the first build. It'll serve at https://voineagvalentin5.github.io/codex-hive-site/. Asset paths are root-absolute, so check it fully only after the custom domain is set, or preview locally with `python3 -m http.server` in `docs/`.
3. **Set the custom domain.** In Settings → Pages → Custom domain, enter `codex-hive.com` (the `docs/CNAME` file already says this). Optional but recommended: verify the domain under GitHub account Settings → Pages → Verified domains. That adds a TXT record `_github-pages-challenge-voineagvalentin5.codex-hive.com` at GoDaddy and blocks domain takeover.
4. **Update DNS at GoDaddy** (Domain → DNS → Manage):
   - Delete the existing apex `@` A record(s) that point to GoDaddy Website Builder, and any conflicting `@` AAAA records.
   - Add 4 A records, `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
   - Optional: add 4 AAAA records, `@` → `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`.
   - Set `www` to a CNAME → `voineagvalentin5.github.io` (replacing GoDaddy's www record). GitHub then redirects www → apex.
   - **Don't touch** the MX, TXT (SPF/DKIM/DMARC) or other records, or the subdomain records (`newz`, `astra`, `academy`, `scribe`, `babble`, etc.). Email and subdomains have to keep working.
5. **Check DNS.** `dig +short codex-hive.com A` should return the 4 GitHub IPs and `dig +short www.codex-hive.com CNAME` should return `voineagvalentin5.github.io.`. Then wait until Settings → Pages says "DNS check successful".
6. **Turn on HTTPS.** Once the certificate is issued (minutes to about 24 h), tick **Enforce HTTPS**.
7. **Check it live.** Go through every page, the nav, /architecture-2 → /technology-stack-draft, /games → /interactive, /apps → /apps-1, and the 404. Check the phone number, the Newz link, the Academy card, the PDFs, and the video and MP3 files. Resubmit `https://codex-hive.com/sitemap.xml` in Google Search Console.
8. **Builder features.** Pick and add the free replacements above (form, analytics, feed) before or right after cutover.

**Rollback:** in GoDaddy DNS, restore the previous `@` A record(s) and the `www` record to their exact pre-cutover values. Record them before step 4 (screenshot the DNS page). Because the GoDaddy builder site is still published, it serves again as soon as DNS propagates, which is fast with a 600 s TTL. Then remove the custom domain in GitHub Pages settings. Nothing in the repo has to be deleted.

Cost: $0. GitHub Pages is free for public repos, and the domain stays registered at GoDaddy as it is now.

## Limits and notes
- `docs/` is about 50 MB (mostly music MP4s). That's within GitHub's limits: no file is over 100 MB, and Pages recommends sites under 1 GB.
- The only external `src` dependencies are 5 suno.com music players on /music, the same as live. There are 0 wsimg.com references left: every GoDaddy image, PDF and media file was downloaded into `docs/assets/`, so after cutover nothing depends on GoDaddy's CDN.
- The screenshots of live include GoDaddy's cookie banner. The home and contact v2 screenshots were re-shot Nov 19 after the About, Contact and divisions changes; the live screenshots and apps-v2 are from earlier the same morning. The v2 screenshots were taken from a local `python3 -m http.server`.

## Update Nov 19, 2026 8:55 AM EST

Decline button enabled (SHOW_DECLINE=True) at Webster's request; rebuilt and retested. Accept grants analytics_storage and persists; Decline stores "denied", hides the banner, and keeps all consent denied. The "Decline" label does not exist on the live GoDaddy banner. Holding for Valentin's cutover decision.
