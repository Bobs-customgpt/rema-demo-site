#!/usr/bin/env python3
"""Build a static mirror of the recycledmaterials.org homepage for the CustomGPT.ai demo.

Keeps ReMA's rendered HTML and theme CSS so the page looks like the real one, saves images,
CSS, JS and video under assets/, strips analytics, ads, tracking pixels and live forms, and
adds the CustomGPT.ai chat agent. Adobe Fonts (Graphie) are licensed per domain, so the
kit is swapped for a Google Fonts lookalike instead of being copied.

Usage: python3 _tools/build.py   (reads _capture/home.html, writes index.html + assets/)
"""
import os, re, subprocess, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.recycledmaterials.org/"
HOST = "www.recycledmaterials.org"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
LOOKALIKE_FONT = "Outfit"

fetched = {}


def fetch(url, dest):
    if url in fetched:
        return fetched[url]
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest) or os.path.getsize(dest) == 0:
        r = subprocess.run(
            ["curl", "-s", "-L", "--compressed", "-A", UA,
             "-H", "Accept: */*", "-H", "Accept-Language: en-US,en;q=0.9",
             "-H", "Referer: " + BASE, "-o", dest, "-w", "%{http_code}", url],
            capture_output=True, text=True)
        ok = r.stdout.strip() == "200" and os.path.exists(dest) and os.path.getsize(dest) > 0
        if not ok:
            print("  FAILED", r.stdout.strip(), url)
            if os.path.exists(dest):
                os.remove(dest)
            fetched[url] = False
            return False
    fetched[url] = True
    return True


def local_for(url):
    """assets/<path> for a recycledmaterials.org URL, else None."""
    u = urllib.parse.urlparse(url)
    if u.netloc not in (HOST, "recycledmaterials.org"):
        return None
    path = urllib.parse.unquote(u.path).lstrip("/")
    if not path or path.endswith("/"):
        return None
    return "assets/" + path


def localize(url, rel_from=""):
    """Download a site asset and return the path to use from a file in rel_from."""
    url = url.strip().strip("'\"")
    if url.startswith("data:") or url.startswith("#"):
        return None
    lp = local_for(url)
    if not lp or not fetch(url, os.path.join(ROOT, lp)):
        return None
    return os.path.relpath(lp, rel_from or ".") if rel_from else lp


def process_css(css_url):
    lp = local_for(css_url)
    dest = os.path.join(ROOT, lp)
    if os.path.exists(dest):
        os.remove(dest)  # always start from ReMA's original CSS so rewrites stay idempotent
    if not fetch(css_url, dest):
        return None
    css = open(dest, encoding="utf-8", errors="ignore").read()
    css_dir = os.path.dirname(lp)

    def repl(m):
        raw = m.group(1).strip().strip("'\"")
        if raw.startswith("data:") or raw.startswith("#"):
            return m.group(0)
        absu = urllib.parse.urljoin(css_url, raw)
        new = localize(absu, css_dir)
        return "url('%s')" % new if new else m.group(0)

    css = re.sub(r"url\(([^)]+)\)", repl, css)
    css = re.sub(r"\bgraphie\b", LOOKALIKE_FONT, css)
    open(dest, "w", encoding="utf-8").write(css)
    return lp


# ---------- scripts: what to keep ----------
KEEP_EXTERNAL = [
    "wp-includes/js/jquery/jquery.min.js", "jquery-migrate.min.js",
    "kb-header-block.min.js", "kb-navigation-block.min.js", "kb-search.min.js",
    "kb-off-canvas-trigger.min.js", "kt-modal-init.min.js", "kb-init-html-bg-video.min.js",
    "kadence/assets/js/navigation.min.js", "splide.min.js", "kb-splide-slider-init.min.js",
    "aos.min.js",
]
KEEP_INLINE = [
    "classList.remove( 'no-js' )", "--scrollbar-offset", "kadenceHeaderConfig",
    "kadenceNavigationConfig", "var kadenceConfig", "var kb_slider", "kadence_aos_params",
    "tribe-no-js", "lets the user close the nav dropdown",
]


def keep_script(tag, body):
    src = re.search(r"\bsrc=['\"]([^'\"]+)", tag)
    if src:
        return any(k in src.group(1) for k in KEEP_EXTERNAL) and "cdnjs" not in src.group(1)
    if "ld+json" in tag:
        return False
    return any(k in body for k in KEEP_INLINE)


def main():
    html = open(os.path.join(ROOT, "_capture/home.html"), encoding="utf-8").read()

    # 1. scripts
    def script_repl(m):
        tag, body = m.group(1), m.group(2)
        if not keep_script(tag, body):
            return ""
        src = re.search(r"\bsrc=['\"]([^'\"]+)", tag)
        if src:
            new = localize(src.group(1))
            if new:
                tag = tag.replace(src.group(1), new)
        return tag + body + "</script>"

    html = re.sub(r"(<script\b[^>]*>)(.*?)</script>", script_repl, html, flags=re.S)
    html = re.sub(r"<noscript>.*?</noscript>", "", html, flags=re.S)

    # 2. head links
    def link_repl(m):
        tag = m.group(0)
        rel = re.search(r"rel=['\"]([^'\"]+)", tag)
        rel = rel.group(1) if rel else ""
        href = re.search(r"href=['\"]([^'\"]+)", tag)
        href = href.group(1) if href else ""
        if rel in ("preload", "dns-prefetch", "EditURI", "alternate", "shortlink",
                   "https://api.w.org/", "preconnect", "prefetch"):
            return ""
        if rel == "stylesheet":
            if "typekit" in href:
                return ('<link rel="preconnect" href="https://fonts.googleapis.com">'
                        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family='
                        + LOOKALIKE_FONT + ':ital,wght@0,300..900;1,300..900&display=swap">')
            if any(k in href for k in ("gravityforms", "search-filter", "filebird")):
                return ""
            lp = process_css(href)
            return tag.replace(href, lp) if lp else tag
        if rel in ("icon", "apple-touch-icon"):
            new = localize(href)
            return tag.replace(href, new) if new else tag
        return tag

    html = re.sub(r"<link\b[^>]*>", link_repl, html)

    # 3. inline <style> blocks: localize url() refs and swap the font
    def style_repl(m):
        css = m.group(2)
        css = re.sub(r"url\(([^)]+)\)",
                     lambda u: ("url('%s')" % localize(u.group(1)))
                     if localize(u.group(1)) else u.group(0), css)
        css = re.sub(r"\bgraphie\b", LOOKALIKE_FONT, css)
        return m.group(1) + css + "</style>"

    html = re.sub(r"(<style\b[^>]*>)(.*?)</style>", style_repl, html, flags=re.S)

    # 4. images, video, inline style backgrounds
    html = re.sub(r'\s(?:srcset|sizes)="[^"]*"', "", html)

    def attr_src(m):
        new = localize(m.group(2))
        return m.group(1) + (new or m.group(2)) + m.group(3)

    html = re.sub(r'(<(?:img|source|video)\b[^>]*?\ssrc=["\'])([^"\']+)(["\'])', attr_src, html)
    html = re.sub(r'(<video\b[^>]*?\sposter=["\'])([^"\']+)(["\'])', attr_src, html)
    html = re.sub(r'(data-(?:bg|src|video)[a-z-]*=["\'])(https://www\.recycledmaterials\.org/[^"\']+)(["\'])',
                  attr_src, html)
    html = re.sub(r"style=\"([^\"]*url\([^\"]*)\"",
                  lambda m: 'style="%s"' % re.sub(
                      r"url\(([^)]+)\)",
                      lambda u: ("url('%s')" % localize(u.group(1))) if localize(u.group(1)) else u.group(0),
                      m.group(1).replace("&#039;", "'")), html)
    html = re.sub(r"\bgraphie\b", LOOKALIKE_FONT, html)

    # 5. links: relative -> real site; forms can't send anything
    html = re.sub(r'href="/(?!/)', 'href="' + BASE, html)
    html = re.sub(r"<form method='post'([^>]*?)id='gform_2' action='/'",
                  r"<form method='post'\1id='gform_2' action='#' onsubmit='event.preventDefault();return false;'",
                  html)

    html = html.replace('<video class="kb-blocks-bg-video"',
                        '<video poster="assets/wp-content/uploads/gradient-bgrd-video-poster.jpg" class="kb-blocks-bg-video"', 1)

    # 6. demo head tags + agent
    html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
    html = re.sub(r'<meta name=["\']robots["\'] content=["\']index[^>]*>', "", html)
    agent = ('\n<link rel="stylesheet" href="demo/demo.css">\n'
             '<script src="config.js"></script>\n<script src="demo/demo.js"></script>\n')
    html = html.replace("</body>", agent + "</body>", 1)

    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    ok = sum(1 for v in fetched.values() if v)
    print("index.html written. assets fetched: %d ok, %d failed" % (ok, len(fetched) - ok))


if __name__ == "__main__":
    main()
