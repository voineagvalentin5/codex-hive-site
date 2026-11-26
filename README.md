# Codex Hive Labs website hub

This repository contains the main Codex Hive website, source snapshots of the
public apps, and the Astra and Earth Resonance Observatory redesign previews.

## Run the main site

```powershell
py -3 -m http.server 8845 --bind 127.0.0.1 --directory docs
```

Open `http://127.0.0.1:8845/`. The main site is static and needs no build step.
The existing GitHub Pages publish root is `docs/`. Its custom domain record is
in `docs/CNAME`.

The Astra and ERO preview folders keep a `CNAME.preview` file only as a reminder
of their public hostnames. Those files are not named `CNAME`, so GitHub Pages
cannot pick them up and cannot hijack `astra.codex-hive.com` or
`ero.codex-hive.com` if the Pages source is ever pointed at the wrong folder.
Do not rename them back to `CNAME` in this repository.

`docs/assets/hub/hub.css` holds the redesigned site styling. Run
`py -3 tools/hub_chrome.py` after changing the shared navigation in that script
to apply it to all pages with the common header. Redirect stubs and embedded
documents use their existing layouts.

## Source map

| Path | Contents |
| --- | --- |
| `docs/` | Main website, its original routes, downloads, media, research, redirects, and the new Media page |
| `manual/` | Existing offline owner’s manual |
| `originals/homepage.html` | Original homepage markup from the recorded baseline commit |
| `sites/` | Public source snapshots for Astra, Academy, Babble, Buzz Newz, Scribe, Earth Resonance Observatory, and CombOS demo |
| `previews/astra/` | One-page Astra redesign with the original instruments available inside the preview |
| `previews/ero/` | Earth Resonance Observatory redesign with the existing NOAA and SOS-70 integrations |
| `sites.json` | Repository URLs, imported commit SHAs, and per-site publish roots |

The app snapshots are outside the main site's Pages directory. Their own build
instructions, licenses, and deployment settings are in each source folder.
For example, Earth Resonance Observatory uses a Next.js export. Serve static
apps from their documented publish root on separate ports so their absolute
paths and service workers operate in the correct scope.

## Try the Astra redesign

```powershell
py -3 -m http.server 8844 --bind 127.0.0.1 --directory previews/astra
```

Open `http://127.0.0.1:8844/`. The main site's Open Hive Astra buttons go to
the public app. The preview has its own entry point for review.

The service intake opens a prefilled email draft. The visitor reviews and
sends it in their email app.

## Try the Earth Resonance Observatory redesign

```powershell
cd previews/ero
npm ci
npm run dev -- --hostname 127.0.0.1 --port 8846
```

Open `http://127.0.0.1:8846/` to use the local Next.js server and its live feeds.
