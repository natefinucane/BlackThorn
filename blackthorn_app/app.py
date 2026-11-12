"""
Cyber risk rating prototype.
Run on your laptop with:   streamlit run app.py
"""
import numpy as np
import streamlit as st

import assumptions as A
import model
import visuals as V

import os
HERE = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(page_title="Blackthorn | Independent cyber risk ratings",
                   page_icon=os.path.join(HERE, "assets", "blackthorn_icon.png"), layout="centered")
WORDMARK = open(os.path.join(HERE, "assets", "blackthorn_wordmark_light.svg")).read()
SEAL = open(os.path.join(HERE, "assets", "blackthorn_seal.svg")).read()
import base64
FONT_B64 = base64.b64encode(open(os.path.join(HERE, "assets", "libre-baskerville-latin-400-normal.woff2"), "rb").read()).decode()

# Brand palette
NIGHT, BARK, SLOE, COPPER, BLOSSOM, HEDGE = "#161311", "#2B2622", "#3F3A66", "#C9874B", "#F6F3EE", "#5E7A5A"
GRADE_COLOURS = {"A": "#4F7A4B", "B": "#7A9A5A", "C": "#C9874B", "D": "#B5582F", "E": "#9E2B25"}
GRADE_TEXT = {"A": BLOSSOM, "B": BLOSSOM, "C": "#1C1916", "D": BLOSSOM, "E": BLOSSOM}

MAT_ICON = {"mfa": ":material/key:", "offline_backups": ":material/backup:",
            "staff_training": ":material/school:", "patching": ":material/system_update:",
            "endpoint_protection": ":material/visibility:", "incident_plan": ":material/assignment:"}

CONTROL_HELP = {
    "mfa": "A second check (a code or app prompt) when logging in. Only answer Yes if it's on for every "
           "email account, remote access and admin login, not just some.",
    "offline_backups": "Copies of your data that an attacker couldn't delete or encrypt, e.g. offline, "
                       "immutable or separate cloud backups, and you've tested restoring from them in the last year.",
    "staff_training": "Everyone has done security or phishing awareness training in the last 12 months.",
    "patching": "Important security updates go on within about a week, e.g. automatic updates are switched on.",
    "endpoint_protection": "Something (or someone) watches for suspicious activity and alerts you, beyond basic antivirus. "
                           "For example a managed detection service.",
    "incident_plan": "A written plan for who does what if you're hit, and you've walked through it at least once.",
}

st.markdown("<style>@font-face {font-family: 'Libre Baskerville'; font-weight: 400; "
            f"src: url(data:font/woff2;base64,{FONT_B64}) format('woff2');}}</style>", unsafe_allow_html=True)
st.markdown("""
<style>
#MainMenu, footer, header [data-testid="stToolbar"] {visibility: hidden;}
.block-container {padding-top: 1.5rem; max-width: 820px;}
h1, h2, h3 {font-family: 'Libre Baskerville', Georgia, serif !important; font-weight: 400 !important; letter-spacing: -0.2px;}
.brandbar {display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2B2622;
           padding-bottom: 12px; margin-bottom: 18px;}
.brandbar svg {height: 34px; width: auto;}
.brandbar .tag {font-size: 13px; color: #B5ABA0;}
.card {border: 1px solid #3A332D; border-radius: 16px; padding: 20px 22px; margin-bottom: 14px; background: #2B2622;}
.grade {border-radius: 14px; text-align: center; padding: 14px 0;}
.grade .g {font-size: 64px; font-weight: 400; line-height: 1; font-family: 'Libre Baskerville', Georgia, serif;}
.grade .l {font-size: 13px; opacity: .9;}
.big {font-size: 18px; line-height: 1.55; color: #E9E3DA;}
.big b {color: #F6F3EE;}
.muted {color: #B5ABA0; font-size: 14px;}
.stat {background: #2B2622; border: 1px solid #3A332D; border-radius: 12px; padding: 12px 14px; height: 100%;}
.stat .v {font-size: 22px; font-weight: 700; color: #F6F3EE;}
.stat .k {font-size: 13px; color: #B5ABA0;}
.step {border-left: 4px solid #C9874B; background: #2B2622; border-radius: 0 12px 12px 0; padding: 14px 18px; margin-bottom: 12px;}
.chip {display: inline-block; background: #1C1916; border: 1px solid #4A413A; color: #E9E3DA; border-radius: 999px;
       padding: 2px 10px; font-size: 13px; margin: 6px 6px 0 0;}
.chip.good {border-color: #5E7A5A; background: rgba(94,122,90,.25);}
.seal svg {width: 92px; height: 92px;}
button[kind="primary"] {color: #1C1916 !important; font-weight: 600 !important;}
</style>
""", unsafe_allow_html=True)


st.markdown(V.CSS, unsafe_allow_html=True)


def brand_bar():
    st.markdown(f"<div class='brandbar'>{WORDMARK}<span class='tag'>Independent cyber risk ratings</span></div>",
                unsafe_allow_html=True)


brand_bar()


def euro(x):
    if x >= 100_000:
        return f"€{round(x, -3):,.0f}"
    return f"€{round(x, -2):,.0f}"


@st.cache_data(show_spinner=False)
def run_rating(name, staff, turnover, sector, controls_tuple):
    biz = {"name": name, "staff": staff, "turnover": turnover, "sector": sector,
           "controls": dict(controls_tuple)}
    return model.rate_business(biz)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("step", 0)
ss.setdefault("name", "")
ss.setdefault("staff", 25)
ss.setdefault("turnover", 2_000_000)
ss.setdefault("sector", "information_communication")
for c in A.CONTROLS:
    ss.setdefault(f"ans_{c}", "Not sure")

# Streamlit forgets the answers on pages that aren't showing, so re-save them every run
for k in ["name", "staff", "turnover", "sector"] + [f"ans_{c}" for c in A.CONTROLS]:
    ss[k] = ss[k]


def go(step):
    ss.step = step


# ---------------------------------------------------------------------------
# Step 0: welcome
# ---------------------------------------------------------------------------
if ss.step == 0:
    st.title("How exposed is your business to a cyber attack?")
    st.markdown(
        "<p class='big'>Answer 10 quick questions and get an independent rating of your cyber risk, "
        "in euro, with the fixes that matter most for a business like yours.</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, ic, v, k, d in [(c1, "clock", "2 minutes", "to answer", "d1"),
                             (c2, "scale", "Independent", "we sell no security products", "d2"),
                             (c3, "lock", "Nothing saved", "your answers stay on screen", "d3")]:
        col.markdown(f"<div class='stat rise {d}'><div class='icw'>{V.icon(ic)}</div>"
                     f"<div><div class='v'>{v}</div><div class='k'>{k}</div></div></div>", unsafe_allow_html=True)
    st.write("")
    st.button("Start", type="primary", on_click=go, args=(1,), width="stretch")
    st.caption("Blackthorn is a prototype built on Irish, UK and international data. Some figures are still estimates. "
               "Named after the wood Irish shillelaghs were cut from: an everyday tool for holding your own ground.")
    st.stop()

# ---------------------------------------------------------------------------
# Step 1: about the business
# ---------------------------------------------------------------------------
if ss.step == 1:
    st.progress(1 / 3, text="Step 1 of 2: about your business")
    st.header("About your business")
    st.text_input("Business name (optional)", key="name", placeholder="Example Payroll Ltd")
    st.number_input("How many people work in the business?", min_value=1, max_value=5000, step=1, key="staff")
    st.number_input("Roughly what's your annual turnover, in euro?", min_value=50_000, max_value=500_000_000,
                    step=50_000, key="turnover")
    st.caption(f"That's €{ss.turnover:,.0f} a year.")
    st.selectbox("Which sector are you in?", list(A.SECTOR_LABELS), key="sector",
                 format_func=lambda k: A.SECTOR_LABELS[k])
    b1, b2 = st.columns(2)
    b1.button("Back", on_click=go, args=(0,), width="stretch")
    b2.button("Next", type="primary", on_click=go, args=(2,), width="stretch")
    st.stop()

# ---------------------------------------------------------------------------
# Step 2: security today
# ---------------------------------------------------------------------------
if ss.step == 2:
    st.progress(2 / 3, text="Step 2 of 2: your security today")
    st.header("Your security today")
    st.markdown("<p class='muted'>Only answer <b>Yes</b> if it's fully in place. "
                "<b>Not sure</b> counts as No, because if nobody knows, it probably isn't working.</p>",
                unsafe_allow_html=True)
    for c in A.CONTROLS:
        st.radio(f"{MAT_ICON[c]} {A.CONTROL_LABELS[c]}", ["Yes", "No", "Not sure"], key=f"ans_{c}",
                 horizontal=True, help=CONTROL_HELP[c])
    b1, b2 = st.columns(2)
    b1.button("Back", on_click=go, args=(1,), width="stretch")
    b2.button("See my rating", type="primary", on_click=go, args=(3,), width="stretch")
    st.stop()

# ---------------------------------------------------------------------------
# Step 3: results
# ---------------------------------------------------------------------------
name = ss.name.strip() or "Your business"
controls = {c: ss[f"ans_{c}"] == "Yes" for c in A.CONTROLS}
with st.spinner("Simulating 100,000 possible years for your business..."):
    r = run_rating(name, int(ss.staff), float(ss.turnover), ss.sector, tuple(sorted(controls.items())))

g = r["grade"]
st.progress(1.0, text="Your rating")

# ---------- rating card ----------
left, right = st.columns([1, 3], vertical_alignment="center")
with left:
    st.markdown(f"<div class='grade pop' style='background:{GRADE_COLOURS[g]};color:{GRADE_TEXT[g]}'>"
                f"<div class='l'>Cyber risk grade</div><div class='g'>{g}</div></div>", unsafe_allow_html=True)
with right:
    n1, n2 = st.columns([3, 1], vertical_alignment="center")
    n1.markdown(f"### {name}")
    n2.markdown(f"<div class='seal pop'>{SEAL}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='big rise d1'>In a typical year you'd expect to lose about <b>{euro(r['expected'])}</b> to cyber incidents. "
        f"But about once in every 100 years, a bad incident could cost <b>{euro(r['p99'])}</b>, "
        f"which is {r['p99_share']:.1%} of your turnover.</p>", unsafe_allow_html=True)

gcol, tcol = st.columns([3, 2], vertical_alignment="center")
with gcol:
    st.markdown(f"<div class='rise d2'>{V.gauge(r['p99_share'])}</div>", unsafe_allow_html=True)
with tcol:
    st.markdown(f"<div class='rise d3'><p style='font-size:15px;color:#E9E3DA;margin:0 0 6px'>"
                f"<b>Where you sit:</b> {A.GRADE_MEANING[g]}</p>"
                f"<p class='muted' style='margin:0'>The needle shows your worst-case (1-in-100) year as a share of turnover. "
                f"Each band is one grade.</p></div>", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
for col, ic, v, k, d in [(s1, "alert", f"{r['p_serious']:.1%}", "chance of a serious incident this year", "d1"),
                         (s2, "clock", f"{r['p_long_outage']:.1%}", "chance of being down for over a week", "d2"),
                         (s3, "euro", euro(r['p95']), "loss in a bad year (1 in 20)", "d3")]:
    col.markdown(f"<div class='stat rise {d}'><div class='icw'>{V.icon(ic)}</div>"
                 f"<div><div class='v'>{v}</div><div class='k'>{k}</div></div></div>", unsafe_allow_html=True)

# ---------- prompt to keep going ----------
af = r["all_fixed"]
if r["fixes"]:
    teaser = (f"<b>Good news:</b> {len(r['fixes'])} fix{'es' if len(r['fixes']) > 1 else ''} could take your worst-case year "
              f"from {euro(r['p99'])} to {euro(af['p99'])}"
              + (f" and your grade from <b>{g}</b> to <b>{af['grade']}</b>." if af["grade"] != g else ".")
              + " <a href='#what-to-do-next'>Jump to what to do</a>")
else:
    teaser = "<b>Nicely done:</b> you have all six core protections. <a href='#what-to-do-next'>See how to keep it that way</a>"
st.markdown(f"<div class='teaser rise d4'>{V.icon('trend_down', 20)}<div>{teaser}</div></div>"
            f"<div class='scrollcue'><span>Scroll to see what this means for your business</span>{V.icon('chevron', 22)}</div>",
            unsafe_allow_html=True)


def section(num, anchor, title, sub):
    st.markdown(f"<div id='{anchor}' class='sechead reveal'><div class='num'>{num}</div>"
                f"<div><h2>{title}</h2><p class='muted'>{sub}</p></div></div>", unsafe_allow_html=True)


def next_link(anchor, text):
    st.markdown(f"<a class='nextlink reveal' href='#{anchor}'>Next: {text} {V.icon('chevron', 18)}</a>",
                unsafe_allow_html=True)


# ---------- 01: the next 100 years ----------
section("01", "your-next-100-years", "Your next 100 years",
        "What the numbers above actually look like, year by year.")
losses = r["losses"]
labels = ["No loss", "Under €10k", "€10k to €50k", "€50k to €250k", "Over €250k"]
edges = [1e-9, 10_000, 50_000, 250_000, np.inf]
shares = [(losses == 0).mean()] + [((losses >= lo) & (losses < hi)).mean() for lo, hi in zip(edges[:-1], edges[1:])]
st.markdown(
    f"<div class='panel reveal'><h4>{V.icon('clock', 18)} If we replayed the next 100 years</h4>"
    f"<div class='sub'>Each square is one simulated year for a business like yours (rounded to whole squares). "
    f"Numbers are years out of 100.</div>{V.waffle(shares, labels)}</div>", unsafe_allow_html=True)
d1, d2 = st.columns(2)
with d1:
    st.markdown(
        f"<div class='panel reveal'><h4>{V.icon('euro', 18)} Where the average loss comes from</h4>"
        f"<div class='sub'>Expected loss per year, by type of incident.</div>"
        f"{V.donut([('Minor (phishing, small frauds)', r['expected_minor'], '#8DA67E'), ('Serious (systems down, data lost)', r['expected_serious'], '#C9874B')], euro(r['expected']), 'a year')}"
        f"</div>", unsafe_allow_html=True)
with d2:
    dt_cols = [("#5E7A5A", "#F6F3EE"), ("#C9874B", "#1C1916"), ("#B5582F", "#F6F3EE")]
    parts = [(lbl, p_, c, tc) for (lbl, p_), (c, tc) in zip(A.DOWNTIME_PROFILE, dt_cols)]
    st.markdown(
        f"<div class='panel reveal'><h4>{V.icon('clock', 18)} If a serious incident hits</h4>"
        f"<div class='sub'>How long businesses are typically disrupted.</div>"
        f"{V.segmented(parts)}</div>", unsafe_allow_html=True)
next_link("how-you-compare", "how you compare to similar firms")

# ---------- 02: compare ----------
section("02", "how-you-compare", "How you compare",
        f"Your protections against other Irish {r['band']} firms.")
rows = []
for c in A.CONTROLS:
    has = controls[c]
    mark = V.icon("check", 16, "#7FA27A", 2.4) if has else V.icon("cross", 16, "#B5582F", 2.4)
    rows.append((f"{V.icon(c, 18)} {A.CONTROL_SHORT[c]} {mark}", r["adoption"][c] * 100,
                 "#7FA27A" if has else "#4A423C"))
freq, sev = r["freq_vs_avg"], r["sev_vs_avg"]
st.markdown(
    f"<div class='panel reveal'><h4>{V.icon('shield', 18)} How common each protection is</h4>"
    f"<div class='sub'>Green bars are protections you have. Grey are ones you don't.</div>"
    f"{V.bars(rows, 100, lambda v: f'{v:.0f}%')}"
    f"<p style='margin:14px 0 0;color:#E9E3DA'>Compared with a typical Irish firm your size, incidents are likely to happen "
    f"<b>{'less' if freq < 1 else 'more'} often</b> ({freq:.1f}x) and cost "
    f"<b>{'less' if sev < 1 else 'more'}</b> ({sev:.1f}x) when they do.</p></div>", unsafe_allow_html=True)
next_link("what-to-do-next", "what to do about it")

# ---------- 03: what to do next ----------
section("03", "what-to-do-next", "What to do next",
        "The fixes that matter most for a business like yours, in order.")
if not r["fixes"]:
    st.success("You have all six core protections in place. Keep testing your backups and your plan every year.")
else:
    st.markdown(
        f"<div class='card reveal'><b>The short version:</b> doing everything below would cost about "
        f"<b>{euro(af['cost'])} a year</b> and cut your 1-in-100 loss from {euro(r['p99'])} to "
        f"<b>{euro(af['p99'])}</b>, moving your grade from <b>{g}</b> to <b>{af['grade']}</b>.</div>",
        unsafe_allow_html=True)
    rows = []
    for step in r["stepdown"]:
        lab = (f"{V.icon('alert', 18)} Today" if step["control"] is None
               else f"{V.icon(step['control'], 18)} + {A.CONTROL_SHORT[step['control']]}")
        rows.append((lab, step["p99"], GRADE_COLOURS[step["grade"]]))
    st.markdown(
        f"<div class='panel reveal'><h4>{V.icon('trend_down', 18)} Your worst-case year, fix by fix</h4>"
        f"<div class='sub'>1-in-100 year loss as each step is added. Bar colour shows the grade.</div>"
        f"{V.bars(rows, r['stepdown'][0]['p99'], euro)}</div>", unsafe_allow_html=True)
    for i, f in enumerate(r["fixes"], 1):
        pays = "Pays for itself on average" if f["return"] >= 1 else "Mainly protects against the worst years"
        good = " good" if f["return"] >= 1 else ""
        st.markdown(
            f"<div class='step reveal'><div style='display:flex;gap:12px;align-items:flex-start'>"
            f"<div style='width:36px;height:36px;border-radius:10px;background:rgba(201,135,75,.15);flex-shrink:0;"
            f"color:#C9874B;display:flex;align-items:center;justify-content:center'>{V.icon(f['control'])}</div>"
            f"<div><b>{i}. {A.CONTROL_ACTION[f['control']]}</b><br>"
            f"<span class='chip'>About {euro(f['cost'])} a year</span>"
            f"<span class='chip'>Cuts your worst-case year by {euro(f['p99_cut'])}</span>"
            f"<span class='chip{good}'>{pays}</span></div></div></div>", unsafe_allow_html=True)
    st.caption("Ranked by how much each step shrinks your worst-case year. We recommend fixes, never suppliers. "
               "Costs are rough estimates for a business your size.")

# ---------- method and finish ----------
st.write("")
with st.expander(":material/menu_book: How we worked this out"):
    st.markdown("""
We simulate 100,000 possible years for a business like yours, counting two kinds of incident:

- **Minor incidents** (a phishing email that gets through, a small fraud): how often and how much from the UK Cyber Security Breaches Survey 2025/26.
- **Serious incidents** (systems down, data destroyed or leaked): how often from the Eurostat / CSO ICT security survey (Ireland, 2024), adjusted because many firms never detect incidents (ESRI 2024); costs from the NetDiligence Cyber Claims Study 2026, scaled to your turnover.
- **Protections:** effects from Marsh McLennan's analysis of insurance claims, reduced because protections overlap. Comparison figures from Eurostat (Ireland 2024) and the MTU / NCSC SME Cyber Resilience report 2025.
- **Downtime:** Sophos State of Ransomware in the UK 2026.

**Still estimates:** how much protections cut costs, what they cost, size scaling and grade thresholds.
This is a prototype for discussion, not financial or insurance advice. Nothing you enter is stored.
""")

c1, c2 = st.columns(2)
c1.button("Change my answers", on_click=go, args=(2,), width="stretch")
c2.button("Start again", on_click=go, args=(0,), width="stretch")

V.reveal_on_scroll()
