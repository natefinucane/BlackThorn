"""
Blackthorn visuals: icons, animated charts and the CSS that drives them.
Everything is plain HTML/SVG + CSS animation, so it needs no extra packages
and works offline. Animations switch off for people who've asked their
device to reduce motion.
"""
import math

NIGHT, BARK, BARK_LINE, SLOE = "#161311", "#2B2622", "#3A332D", "#3F3A66"
COPPER, BLOSSOM, MUTED, HEDGE = "#C9874B", "#F6F3EE", "#B5ABA0", "#5E7A5A"
GRADE_COLOURS = {"A": "#4F7A4B", "B": "#7A9A5A", "C": "#C9874B", "D": "#B5582F", "E": "#9E2B25"}
GRADE_TEXT = {"A": BLOSSOM, "B": BLOSSOM, "C": "#1C1916", "D": BLOSSOM, "E": BLOSSOM}

# ---------------------------------------------------------------------------
# Icons (24 x 24 outline, drawn in the current text colour)
# ---------------------------------------------------------------------------
_ICON_PATHS = {
    "mfa": '<circle cx="7.5" cy="15.5" r="3.5"/><path d="M10 13 L20 3 M16 7 L19 10 M13.5 9.5 L16 12"/>',
    "offline_backups": '<ellipse cx="12" cy="5.5" rx="7" ry="2.5"/><path d="M5 5.5v6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-6 M5 11.5v6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-6"/>',
    "staff_training": '<path d="M2 9.5l10-5 10 5-10 5z M6 11.5v4.5c0 1.6 2.7 3 6 3s6-1.4 6-3v-4.5 M22 9.5v5"/>',
    "patching": '<path d="M20 11a8 8 0 0 0-14.3-4.8 M4 3.5v4h4 M4 13a8 8 0 0 0 14.3 4.8 M20 20.5v-4h-4"/>',
    "endpoint_protection": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "incident_plan": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2.5h6V4 M9 10h6 M9 14h6 M9 18h3"/>',
    "alert": '<path d="M12 3.5l9.5 17h-19z M12 10v4.5 M12 17.5v.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "euro": '<path d="M17.5 6.5a7 7 0 1 0 0 11 M4 10h9 M4 14h9"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.6-3.4 8-8 9-4.6-1-8-4.4-8-9V6z M8.5 12l2.5 2.5 4.5-4.5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "scale": '<path d="M12 4v16 M7 20h10 M4 8h16 M4 8l-2.5 6a3 3 0 0 0 5 0z M20 8l-2.5 6a3 3 0 0 0 5 0z"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "cross": '<path d="M6 6l12 12 M18 6L6 18"/>',
    "trend_down": '<path d="M3 7l6 6 4-4 8 8 M21 11v6h-6"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
}


def icon(name, size=20, colour="currentColor", stroke=1.8):
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{colour}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{_ICON_PATHS[name]}</svg>')


# ---------------------------------------------------------------------------
# CSS: brand components + animations
# ---------------------------------------------------------------------------
CSS = f"""
<style>
@keyframes rise {{ from {{opacity: 0; transform: translateY(12px);}} to {{opacity: 1; transform: none;}} }}
@keyframes pop {{ 0% {{opacity: 0; transform: scale(.6);}} 70% {{transform: scale(1.06);}} 100% {{opacity: 1; transform: scale(1);}} }}
@keyframes grow {{ from {{width: 0;}} }}
@keyframes needle {{ from {{transform: rotate(-90deg);}} to {{transform: rotate(var(--a));}} }}
@keyframes dash {{ from {{stroke-dasharray: 0 400;}} }}
@keyframes fadein {{ from {{opacity: 0;}} to {{opacity: 1;}} }}

.rise {{animation: rise .6s ease-out both;}}
.d1 {{animation-delay: .1s;}} .d2 {{animation-delay: .2s;}} .d3 {{animation-delay: .3s;}} .d4 {{animation-delay: .4s;}}
.pop {{animation: pop .7s cubic-bezier(.2,.8,.3,1.2) both;}}

.ic {{vertical-align: -4px; flex-shrink: 0;}}
.stat {{display: flex; gap: 12px; align-items: flex-start;}}
.stat .icw {{width: 38px; height: 38px; border-radius: 10px; background: rgba(201,135,75,.15); color: {COPPER};
            display: flex; align-items: center; justify-content: center;}}

/* gauge */
.gauge svg {{width: 100%; height: auto; display: block;}}
.gauge .needle {{transform-origin: 150px 150px; animation: needle 1.4s cubic-bezier(.3,1.4,.5,1) .3s both;}}

/* bars */
.bars .row {{display: grid; grid-template-columns: 170px 1fr 70px; gap: 10px; align-items: center; margin: 9px 0;}}
.bars .lab {{font-size: 14px; color: #E9E3DA; display: flex; gap: 8px; align-items: center;}}
.bars .track {{background: #1C1916; border-radius: 6px; height: 22px; overflow: hidden; position: relative;}}
.bars .fill {{height: 100%; border-radius: 6px; animation: grow 1.1s ease-out both;}}
.bars .val {{font-size: 14px; color: {BLOSSOM}; text-align: right; font-variant-numeric: tabular-nums;}}

/* waffle */
.waffle {{display: grid; grid-template-columns: repeat(20, 1fr); gap: 4px; max-width: 520px;}}
.waffle span {{aspect-ratio: 1; border-radius: 3px; animation: fadein .35s ease-out both;}}
.legend {{display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 12px; font-size: 13px; color: #E9E3DA;}}
.legend i {{display: inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: 6px; vertical-align: -1px;}}

/* donut */
.donut circle.arc {{animation: dash 1.1s ease-out both;}}

/* segmented bar */
.seg {{display: flex; height: 26px; border-radius: 8px; overflow: hidden; animation: grow 1.2s ease-out both;}}
.seg div {{display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;}}

.panel {{background: {BARK}; border: 1px solid {BARK_LINE}; border-radius: 16px; padding: 18px 20px; margin-bottom: 14px;}}
.panel h4 {{margin: 0 0 4px; font-size: 16px; font-weight: 600; color: {BLOSSOM}; font-family: inherit !important;}}
.panel .sub {{font-size: 13px; color: {MUTED}; margin-bottom: 10px;}}

/* scrolling story */
@keyframes bob {{ 0%, 100% {{transform: translateY(0);}} 50% {{transform: translateY(6px);}} }}
html, [data-testid="stMain"] {{scroll-behavior: smooth;}}
.teaser {{display: flex; gap: 12px; align-items: flex-start; background: rgba(94,122,90,.18); border: 1px solid #5E7A5A;
          border-radius: 14px; padding: 14px 18px; margin: 18px 0 6px; color: #E9E3DA; font-size: 15px; line-height: 1.5;}}
.teaser .ic {{color: #8DA67E; margin-top: 2px;}}
.teaser a, .nextlink {{color: {COPPER} !important; text-decoration: none; font-weight: 600;}}
.teaser a:hover, .nextlink:hover {{text-decoration: underline;}}
.scrollcue {{display: flex; flex-direction: column; align-items: center; color: {MUTED}; font-size: 13px; margin: 26px 0 8px;}}
.scrollcue .ic {{color: {COPPER}; animation: bob 1.6s ease-in-out infinite;}}
.sechead {{display: flex; gap: 16px; align-items: flex-start; margin: 46px 0 14px; padding-top: 22px;
           border-top: 1px solid {BARK_LINE}; scroll-margin-top: 20px;}}
.sechead .num {{font-family: 'Libre Baskerville', Georgia, serif; font-size: 30px; color: {COPPER}; line-height: 1.1;}}
.sechead h2 {{margin: 0 !important; padding: 0 !important; font-size: 26px !important;}}
.sechead p {{margin: 4px 0 0;}}
.nextlink {{display: flex; align-items: center; justify-content: center; gap: 6px; margin: 18px 0 0; font-size: 15px;}}

/* reveal on scroll: plain on-load animation unless the scroll script is running */
.reveal {{animation: rise .7s ease-out both;}}
.js-reveal .reveal, .js-reveal .reveal * {{animation-play-state: paused;}}
.js-reveal .reveal.in, .js-reveal .reveal.in * {{animation-play-state: running;}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{animation: none !important; transition: none !important;}}
  html, [data-testid="stMain"] {{scroll-behavior: auto;}}
  .gauge .needle {{transform: rotate(var(--a));}}
}}
</style>
"""

# ---------------------------------------------------------------------------
# Risk gauge: five equal bands A to E, needle shows where this firm sits
# ---------------------------------------------------------------------------
BAND_EDGES = [0, 0.02, 0.05, 0.10, 0.20, 0.40]   # share of turnover


def _angle_for(share):
    for i in range(5):
        lo, hi = BAND_EDGES[i], BAND_EDGES[i + 1]
        if share < hi or i == 4:
            f = min(max((share - lo) / (hi - lo), 0), 1)
            return (i + f) * 36 - 90
    return 90


def gauge(share):
    cx, cy, r = 150, 150, 112
    arcs, labels = [], []
    for i, g in enumerate("ABCDE"):
        a0, a1 = math.radians(180 + i * 36 + 1.2), math.radians(180 + (i + 1) * 36 - 1.2)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        arcs.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f}" stroke="{GRADE_COLOURS[g]}" '
                    f'stroke-width="26" fill="none" stroke-linecap="butt"/>')
        am = math.radians(180 + (i + .5) * 36)
        lx, ly = cx + (r + 30) * math.cos(am), cy + (r + 30) * math.sin(am)
        labels.append(f'<text x="{lx:.1f}" y="{ly + 5:.1f}" text-anchor="middle" font-size="15" '
                      f'font-family="Libre Baskerville, Georgia, serif" fill="{MUTED}">{g}</text>')
    ticks = []
    for i, edge in enumerate(BAND_EDGES[1:5], 1):
        a = math.radians(180 + i * 36)
        tx, ty = cx + (r - 26) * math.cos(a), cy + (r - 26) * math.sin(a)
        ticks.append(f'<text x="{tx:.1f}" y="{ty + 4:.1f}" text-anchor="middle" font-size="10" fill="{MUTED}">'
                     f'{edge:.0%}</text>')
    ang = _angle_for(share)
    needle = (f'<g class="needle" style="--a:{ang:.1f}deg">'
              f'<path d="M146,150 L150,52 L154,150 Z" fill="{BLOSSOM}"/></g>'
              f'<circle cx="150" cy="150" r="11" fill="{BLOSSOM}"/><circle cx="150" cy="150" r="4.5" fill="{COPPER}"/>')
    return (f'<div class="gauge"><svg viewBox="0 0 300 175" role="img" aria-label="Risk gauge">'
            f'{"".join(arcs)}{"".join(labels)}{"".join(ticks)}{needle}</svg></div>')


# ---------------------------------------------------------------------------
# Animated horizontal bars
# ---------------------------------------------------------------------------
def bars(rows, max_value, fmt):
    """rows: list of (label_html, value, colour)."""
    out = ['<div class="bars">']
    for i, (lab, v, colour) in enumerate(rows):
        w = 0 if max_value <= 0 else max(v / max_value * 100, 1.5)
        out.append(f'<div class="row"><div class="lab">{lab}</div><div class="track">'
                   f'<div class="fill" style="width:{w:.1f}%;background:{colour};animation-delay:{.15 * i:.2f}s"></div>'
                   f'</div><div class="val">{fmt(v)}</div></div>')
    out.append("</div>")
    return "".join(out)


# ---------------------------------------------------------------------------
# 100-year waffle: one square per simulated year
# ---------------------------------------------------------------------------
WAFFLE_COLOURS = ["#5E7A5A", "#8DA67E", "#D8B27A", COPPER, "#B5582F"]


def _hundred(shares):
    """Largest-remainder rounding so the squares add up to exactly 100."""
    raw = [s * 100 for s in shares]
    base = [int(x) for x in raw]
    rem = 100 - sum(base)
    order = sorted(range(len(raw)), key=lambda i: raw[i] - base[i], reverse=True)
    for i in order[:rem]:
        base[i] += 1
    return base


def waffle(shares, labels):
    counts = _hundred(shares)
    cells, k = [], 0
    for colour, n in zip(WAFFLE_COLOURS, counts):
        for _ in range(n):
            cells.append(f'<span style="background:{colour};animation-delay:{k * 0.012:.3f}s"></span>')
            k += 1
    legend = "".join(
        f'<div><i style="background:{c}"></i>{lab}: <b>{s * 100:.1f}</b></div>'
        for c, lab, s in zip(WAFFLE_COLOURS, labels, shares))
    return f'<div class="waffle">{"".join(cells)}</div><div class="legend">{legend}</div>'


# ---------------------------------------------------------------------------
# Donut: where the expected loss comes from
# ---------------------------------------------------------------------------
def donut(parts, centre_top, centre_bottom):
    """parts: list of (label, value, colour)."""
    r, c = 52, 2 * math.pi * 52
    total = sum(v for _, v, _ in parts) or 1
    out, offset = [], 0
    for i, (_, v, colour) in enumerate(parts):
        length = v / total * c
        out.append(f'<circle class="arc" cx="70" cy="70" r="{r}" fill="none" stroke="{colour}" stroke-width="18" '
                   f'stroke-dasharray="{length:.1f} {c:.1f}" stroke-dashoffset="{-offset:.1f}" '
                   f'style="animation-delay:{.2 + .5 * i:.1f}s" '
                   f'transform="rotate(-90 70 70)"/>')
        offset += length
    legend = "".join(f'<div><i style="background:{col}"></i>{lab}: <b>{v / total:.0%}</b></div>'
                     for lab, v, col in parts)
    return (f'<div class="donut" style="display:flex;gap:18px;align-items:center;flex-wrap:wrap">'
            f'<svg width="140" height="140" viewBox="0 0 140 140">'
            f'<circle cx="70" cy="70" r="{r}" fill="none" stroke="#1C1916" stroke-width="18"/>{"".join(out)}'
            f'<text x="70" y="68" text-anchor="middle" font-size="17" font-weight="700" fill="{BLOSSOM}">{centre_top}</text>'
            f'<text x="70" y="86" text-anchor="middle" font-size="10.5" fill="{MUTED}">{centre_bottom}</text></svg>'
            f'<div class="legend" style="flex-direction:column;margin:0">{legend}</div></div>')


# ---------------------------------------------------------------------------
# Segmented bar for downtime
# ---------------------------------------------------------------------------
def segmented(parts):
    """parts: list of (label, share, colour, text_colour)."""
    segs = "".join(f'<div style="width:{s * 100:.1f}%;background:{c};color:{tc}">{s:.0%}</div>'
                   for _, s, c, tc in parts)
    legend = "".join(f'<div><i style="background:{c}"></i>{lab}</div>' for lab, _, c, _ in parts)
    return f'<div class="seg">{segs}</div><div class="legend">{legend}</div>'


# ---------------------------------------------------------------------------
# Scroll script: starts each section's animation when it scrolls into view,
# and makes the "Next" links glide smoothly. If it can't run, everything
# simply animates on page load instead.
# ---------------------------------------------------------------------------
_REVEAL_JS = """
<script>
(function () {
  try {
    const w = window.parent, doc = w.document;
    if (!("IntersectionObserver" in w)) return;
    doc.documentElement.classList.add("js-reveal");
    if (!w.__btReveal) {
      w.__btReveal = new w.IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add("in"); w.__btReveal.unobserve(e.target); }
        });
      }, { threshold: 0.15 });
      const bind = function () {
        doc.querySelectorAll(".reveal:not([data-bt])").forEach(function (el) {
          el.setAttribute("data-bt", "1"); w.__btReveal.observe(el);
        });
      };
      bind();
      new w.MutationObserver(bind).observe(doc.body, { childList: true, subtree: true });
      doc.addEventListener("click", function (ev) {
        const a = ev.target.closest && ev.target.closest("a[href^='#']");
        if (!a) return;
        const t = doc.getElementById(a.getAttribute("href").slice(1));
        if (t) { ev.preventDefault(); t.scrollIntoView({ behavior: "smooth", block: "start" }); }
      });
    }
  } catch (err) { /* fall back to plain animations */ }
})();
</script>
"""


def reveal_on_scroll():
    import streamlit.components.v1 as components
    components.html(_REVEAL_JS, height=0)
