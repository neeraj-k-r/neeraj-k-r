import json
import math
import os
from collections import defaultdict
from datetime import datetime
from html import escape

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATS_PATH = os.path.join(BASE_DIR, "data", "github_stats.json")
CARDS_DIR = os.path.join(BASE_DIR, "cards")

PAPER = "#0D1117"
PAPER_ALT = "#161B22"
INK = "#F0F6FC"
INK_SOFT = "#9EAAB6"
INK_MUTED = "#6E7681"
RULE = "#30363D"
ZORO = "#22C55E"
ZORO_GLOW = "#4ADE80"

FONT_SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"


def load_stats():
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(contributions):
    total = 0
    active_days = 0
    cur_streak = 0
    longest_streak = 0
    busiest_count = 0
    busiest_date = ""
    monthly = defaultdict(int)

    for day in contributions:
        c = int(day.get("count", 0))
        d = day.get("date", "")
        total += c
        if c > 0:
            active_days += 1
            cur_streak += 1
            if cur_streak > longest_streak:
                longest_streak = cur_streak
        else:
            cur_streak = 0

        if c > busiest_count:
            busiest_count = c
            busiest_date = d

        if len(d) >= 7:
            monthly[d[:7]] += c

    sorted_months = sorted(monthly.items())[-12:]
    return {
        "total": total,
        "active_days": active_days,
        "longest_streak": longest_streak,
        "busiest_count": busiest_count,
        "busiest_date": busiest_date,
        "monthly": sorted_months,
    }


def write_svg(filename, content):
    os.makedirs(CARDS_DIR, exist_ok=True)
    path = os.path.join(CARDS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {filename}")


def render_hero(stats):
    zoro_path = os.path.join(BASE_DIR, "data", "zoro_dots.json")
    dots = []
    if os.path.exists(zoro_path):
        with open(zoro_path, "r", encoding="utf-8") as f:
            zdata = json.load(f)
        cols = zdata.get("cols", 56)
        rows = zdata.get("rows", 48)
        spacing = 3.35
        cx0 = 745 + (222 - (cols - 1) * spacing) / 2
        cy0 = 26 + (168 - (rows - 1) * spacing) / 2
        for c, r, rad, val in zdata.get("dots", []):
            x = round(cx0 + c * spacing, 1)
            y = round(cy0 + r * spacing, 1)
            if isinstance(val, str) and val.startswith("#"):
                dots.append(f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{val}"/>')
            else:
                dot_color = ZORO_GLOW if r < 16 else (ZORO if r < 30 else INK)
                dots.append(
                    f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{dot_color}" opacity="{val}"/>'
                )
    else:
        cols, rows = 14, 10
        cx0, cy0 = 765, 36
        spacing = 14
        for r in range(rows):
            for c in range(cols):
                x = cx0 + c * spacing
                y = cy0 + r * spacing
                dots.append(f'<circle cx="{x}" cy="{y}" r="1.2" fill="{ZORO}" opacity="0.25"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 220" width="1000" height="220" role="img" aria-label="Neeraj K R — Full-Stack Engineer &amp; Creator of Portfoolio">
  <style>
    .blink {{ animation: pulse 2.2s ease-in-out infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} }}
    .scan {{ animation: scan 5s ease-in-out infinite; }}
    @keyframes scan {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(130px); }} }}
  </style>
  <rect x="2" y="2" width="996" height="216" rx="12" fill="{PAPER}" stroke="{RULE}" stroke-width="2"/>
  <rect x="16" y="16" width="968" height="188" rx="8" fill="none" stroke="{RULE}" stroke-width="1" opacity="0.6"/>

  <circle cx="42" cy="44" r="4.5" fill="{ZORO_GLOW}" class="blink"/>
  <text x="56" y="48" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="1.6" fill="{ZORO_GLOW}">LIVE · NEERAJKR.PORTFOOLIO.ME</text>

  <text x="38" y="102" font-family="{FONT_SANS}" font-size="44" font-weight="900" letter-spacing="-1.5" fill="{INK}">NEERAJ K R</text>
  <text x="38" y="134" font-family="{FONT_SANS}" font-size="17" font-weight="600" fill="{INK_SOFT}">Full-Stack Engineer &amp; Creator of Portfoolio</text>
  <text x="38" y="164" font-family="{FONT_MONO}" font-size="12.5" fill="{INK_MUTED}">Building developer tools, autonomous agents &amp; edge-rendered web apps · Kerala, IN</text>

  <rect x="745" y="26" width="222" height="168" rx="8" fill="{PAPER_ALT}" stroke="{ZORO}" stroke-width="1.2" stroke-opacity="0.45"/>
  {"".join(dots)}
  <line x1="748" y1="32" x2="964" y2="32" stroke="{ZORO_GLOW}" stroke-width="1.2" opacity="0.35" class="scan"/>
</svg>'''
    write_svg("hero.svg", svg)


def render_heatmap(stats, metrics):
    contributions = stats.get("contributions", [])
    # Keep last 53 weeks (371 days max)
    days = contributions[-371:]
    rects = []
    level_colors = {
        0: "#161B22",
        1: "#0E4429",
        2: "#006D32",
        3: "#26A641",
        4: "#39D353",
    }

    cell = 14
    gap = 4
    start_x = 34
    start_y = 58

    month_labels = []
    last_month = ""
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for idx, day in enumerate(days):
        col = idx // 7
        row = idx % 7
        x = start_x + col * (cell + gap)
        y = start_y + row * (cell + gap)
        lvl = int(day.get("level", 0))
        color = level_colors.get(lvl, "#161B22")
        rects.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{color}"/>')

        d_str = day.get("date", "")
        if row == 0 and len(d_str) >= 7:
            ym = d_str[:7]
            if ym != last_month:
                m_num = int(d_str[5:7])
                month_labels.append(
                    f'<text x="{x}" y="47" font-family="{FONT_MONO}" font-size="10" fill="{INK_MUTED}">{month_names[m_num]}</text>'
                )
                last_month = ym

    total_str = f"{metrics['total']:,}"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 196" width="1000" height="196" role="img" aria-label="Contribution graph for the last 12 months">
  <rect x="2" y="2" width="996" height="192" rx="12" fill="{PAPER}" stroke="{RULE}" stroke-width="2"/>
  <text x="34" y="29" font-family="{FONT_MONO}" font-size="11.5" font-weight="700" letter-spacing="1.4" fill="{INK}">CONTRIBUTION GRAPH · LAST 12 MONTHS</text>
  <text x="966" y="29" text-anchor="end" font-family="{FONT_MONO}" font-size="11.5" font-weight="700" fill="{ZORO_GLOW}">{total_str} CONTRIBUTIONS</text>
  {"".join(month_labels)}
  {"".join(rects)}
</svg>'''
    write_svg("heatmap.svg", svg)


def render_activity(metrics):
    monthly = metrics["monthly"]
    max_val = max([v for _, v in monthly] + [1])
    bars = []
    bar_w = 24
    gap = 10
    base_x = 560
    base_y = 122
    max_h = 68

    for i, (ym, val) in enumerate(monthly):
        h = max(4, int((val / max_val) * max_h))
        x = base_x + i * (bar_w + gap)
        y = base_y - h
        m_label = ym[5:7]
        fill = ZORO_GLOW if val == max_val else "#238636"
        bars.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" rx="3" fill="{fill}"/>')
        bars.append(
            f'<text x="{x + bar_w / 2}" y="138" text-anchor="middle" font-family="{FONT_MONO}" font-size="9" fill="{INK_MUTED}">{m_label}</text>'
        )

    b_date = metrics["busiest_date"] or "N/A"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 156" width="1000" height="156" role="img" aria-label="Contributions by month and streaks">
  <rect x="2" y="2" width="996" height="152" rx="12" fill="{PAPER}" stroke="{RULE}" stroke-width="2"/>
  <text x="34" y="30" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="1.4" fill="{ZORO}">ACTIVITY METRICS</text>

  <text x="34" y="76" font-family="{FONT_SANS}" font-size="30" font-weight="900" fill="{INK}">{metrics["total"]:,}</text>
  <text x="34" y="96" font-family="{FONT_MONO}" font-size="10.5" fill="{INK_MUTED}">TOTAL (12M)</text>

  <text x="174" y="76" font-family="{FONT_SANS}" font-size="30" font-weight="900" fill="{ZORO_GLOW}">{metrics["longest_streak"]}d</text>
  <text x="174" y="96" font-family="{FONT_MONO}" font-size="10.5" fill="{INK_MUTED}">LONGEST STREAK</text>

  <text x="304" y="76" font-family="{FONT_SANS}" font-size="30" font-weight="900" fill="{INK}">{metrics["active_days"]}</text>
  <text x="304" y="96" font-family="{FONT_MONO}" font-size="10.5" fill="{INK_MUTED}">ACTIVE DAYS</text>

  <text x="424" y="76" font-family="{FONT_SANS}" font-size="30" font-weight="900" fill="{INK}">{metrics["busiest_count"]}</text>
  <text x="424" y="96" font-family="{FONT_MONO}" font-size="10.5" fill="{INK_MUTED}">BEST ({b_date})</text>

  <line x1="534" y1="24" x2="534" y2="132" stroke="{RULE}" stroke-width="1"/>
  <text x="560" y="30" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="1.4" fill="{ZORO}">MONTHLY CADENCE</text>
  {"".join(bars)}
</svg>'''
    write_svg("activity.svg", svg)


def render_mini_stat(filename, kicker, big_val, sub, aria):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 112" width="330" height="112" role="img" aria-label="{escape(aria)}">
  <rect x="2" y="2" width="326" height="108" rx="12" fill="{PAPER}" stroke="{RULE}" stroke-width="2"/>
  <text x="22" y="28" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" letter-spacing="1.4" fill="{ZORO}">{escape(kicker)}</text>
  <text x="22" y="66" font-family="{FONT_SANS}" font-size="24" font-weight="900" fill="{INK}">{escape(big_val)}</text>
  <text x="22" y="90" font-family="{FONT_MONO}" font-size="11" fill="{INK_SOFT}">{escape(sub)}</text>
</svg>'''
    write_svg(filename, svg)


def render_title_building():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 54" width="1000" height="54" role="img" aria-label="What I am building">
  <rect x="2" y="4" width="996" height="46" rx="10" fill="{PAPER_ALT}" stroke="{ZORO}" stroke-width="1.5"/>
  <text x="26" y="32" font-family="{FONT_MONO}" font-size="13" font-weight="700" letter-spacing="2" fill="{ZORO_GLOW}">WHAT I&apos;M BUILDING</text>
  <text x="974" y="32" text-anchor="end" font-family="{FONT_MONO}" font-size="11" fill="{INK_SOFT}">SHIPPED &amp; IN PRODUCTION →</text>
</svg>'''
    write_svg("title-building.svg", svg)


def render_repo_card(filename, title, stack, desc1, desc2, url_label):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 148" width="330" height="148" role="img" aria-label="{escape(title)}">
  <rect x="2" y="2" width="326" height="144" rx="12" fill="{PAPER}" stroke="{RULE}" stroke-width="2"/>
  <text x="22" y="32" font-family="{FONT_SANS}" font-size="18" font-weight="900" fill="{INK}">{escape(title)}</text>
  <text x="308" y="32" text-anchor="end" font-family="{FONT_MONO}" font-size="10.5" font-weight="700" fill="{ZORO_GLOW}">{escape(stack)}</text>
  <line x1="22" y1="44" x2="308" y2="44" stroke="{RULE}" stroke-width="1"/>
  <text x="22" y="72" font-family="{FONT_SANS}" font-size="12.5" fill="{INK_SOFT}">{escape(desc1)}</text>
  <text x="22" y="92" font-family="{FONT_SANS}" font-size="12.5" fill="{INK_SOFT}">{escape(desc2)}</text>
  <text x="22" y="126" font-family="{FONT_MONO}" font-size="11" font-weight="700" fill="{ZORO}">{escape(url_label)} ↗</text>
</svg>'''
    write_svg(filename, svg)


def render_skills():
    rows = [
        ("LANGUAGES", "JavaScript (ES6+) · TypeScript · Python · SQL · HTML5 · CSS3"),
        ("FRONTEND", "React · Next.js · Tailwind CSS · Responsive UI · SVG & Canvas"),
        ("BACKEND & EDGE", "Node.js · Express · Cloudflare Workers · REST APIs · SSR"),
        ("CLOUD & DATA", "Supabase · PostgreSQL · MongoDB · Netlify · GitHub Actions · Docker"),
        ("AI & AGENTS", "LLM Workflows · Multi-Agent Systems · Prompt Engineering · IBM Cloud"),
    ]
    lines = []
    y = 60
    for cat, items in rows:
        lines.append(
            f'<text x="34" y="{y}" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="1.1" fill="{ZORO_GLOW}">{escape(cat)}</text>'
        )
        lines.append(
            f'<text x="195" y="{y}" font-family="{FONT_SANS}" font-size="13" font-weight="500" fill="{INK_SOFT}">{escape(items)}</text>'
        )
        y += 26

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 186" width="1000" height="186" role="img" aria-label="Skills and stack">
  <rect x="2" y="2" width="996" height="182" rx="12" fill="{PAPER}" stroke="{RULE}" stroke-width="2"/>
  <text x="34" y="30" font-family="{FONT_MONO}" font-size="11" font-weight="700" letter-spacing="1.4" fill="{ZORO}">SKILLS &amp; TECHNICAL STACK</text>
  <line x1="34" y1="40" x2="966" y2="40" stroke="{RULE}" stroke-width="1"/>
  {"".join(lines)}
</svg>'''
    write_svg("skills.svg", svg)


def main():
    stats = load_stats()
    metrics = compute_metrics(stats.get("contributions", []))

    render_hero(stats)
    render_heatmap(stats, metrics)
    render_activity(metrics)

    render_mini_stat(
        "build.svg",
        "SHIPPED",
        f"{stats.get('public_repo_count', 16)} PUBLIC REPOS",
        "JavaScript · TypeScript · Python",
        "Public repositories shipped",
    )
    render_mini_stat(
        "portfoolio.svg",
        "FLAGSHIP",
        "PORTFOOLIO.ME",
        "Free Portfolio Maker & Hosting",
        "Portfoolio Portfolio Maker",
    )
    render_mini_stat(
        "stars.svg",
        "YEARLY OUTPUT",
        f"{metrics['total']:,} COMMITS",
        f"{metrics['longest_streak']}d streak · {metrics['active_days']} active days",
        "Yearly contributions and streak",
    )

    render_title_building()

    render_repo_card(
        "repo-portfoolio.svg",
        "Portfoolio",
        "JS · CLOUDFLARE",
        "Developer portfolio maker &",
        "wildcard *.portfoolio.me hosting.",
        "portfoolio.me",
    )
    render_repo_card(
        "repo-akshaya.svg",
        "Akshaya-Sahayi",
        "JS · ★ 2",
        "Digital civic & citizen service",
        "helper built for local access.",
        "github.com/neeraj-k-r/AKSHAYA-SAHAYI",
    )
    render_repo_card(
        "repo-campusbridge.svg",
        "CampusBridge",
        "JS · ★ 2",
        "Student & campus resource",
        "collaboration platform.",
        "github.com/neeraj-k-r/campusbridge",
    )

    render_skills()


if __name__ == "__main__":
    main()
