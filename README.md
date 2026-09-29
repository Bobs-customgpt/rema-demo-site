# Recycled Materials Association (ReMA): Demo Site

A static replica of the [recycledmaterials.org homepage](https://www.recycledmaterials.org/), built for the CustomGPT.ai website-agent demo to ReMA (Paul Hartgen). It is ReMA's own rendered homepage markup and theme CSS, saved as static files, with the live "Ask ReMA" CustomGPT.ai agent added as a floating chat.

Not affiliated with or endorsed by the Recycled Materials Association. Internal sales demo only; do not present it as ReMA's real site. Content was captured from the public homepage on 2026-09-29. The page is `noindex, nofollow` and `robots.txt` blocks crawlers.

## What changed vs. the live homepage
- **Agent:** CustomGPT project 101035 ("REMA Demo") via `chat.js`, set in `config.js`. Override for a test with `index.html?p_id=...&p_key=...`.
- **Removed:** analytics and tag managers (GA4, GTM, Adobe Launch, LinkedIn Insight), Multiview/Adzerk ad slots (the empty rows are collapsed in `demo/demo.css`), Search & Filter, Gravity Forms scripts, emoji and speculation scripts.
- **Newsletter form:** the markup is kept but submitting it does nothing; no data leaves the page.
- **Font:** ReMA uses Graphie from Adobe Fonts, which is licensed per domain, so it is swapped for Outfit (Google Fonts), a close lookalike.
- **Background video:** re-encoded from 4K (22 MB) to 1920px (1.3 MB) with a poster frame.
- **Links:** every nav, button and footer link goes to the real recycledmaterials.org page.

## Structure
- `index.html`: the homepage (generated, don't hand-edit; rebuild instead)
- `config.js`: agent `p_id` / `p_key`
- `demo/demo.js`, `demo/demo.css`: agent loader and the few demo overrides
- `assets/`: ReMA's theme CSS, JS, images and video, mirrored under their original paths
- `_tools/build.py`: rebuilds `index.html` + `assets/` from `_capture/home.html` (`_capture/` holds the raw capture and screenshots and stays local)

## Rebuild from a fresh capture
```bash
curl -s -L --compressed -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36" -H "Accept: text/html" -o _capture/home.html https://www.recycledmaterials.org/
python3 _tools/build.py
```

## Local preview
```bash
python3 -m http.server 8093
```

## Hosting
GitHub Pages from `main` (root). Push to `main` to redeploy.
