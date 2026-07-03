def render_svg(data):
    techs = data.get("technologies", [])
    complexity = data.get("complexity", [])
    profile = data.get("profile", {})
    network = data.get("network", [])
    generated = data.get("generated", "")

    def fmt(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")

    def dot(color):
        return f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{color};flex-shrink:0;vertical-align:middle;"></span>'

    tech_cards = []
    for i, t in enumerate(techs):
        d = round(0.15 + i * 0.1, 2)
        tech_cards.append(f"""
    <div class="tc" style="animation: fadeIn 0.5s ease-out {d}s both;">
      <div class="tca" style="background:{t['level_color']}"></div>
      <span class="tcn">{t['name']}</span>
      <span class="tcl" style="color:{t['level_color']}">{t['level']}</span>
      <div class="tcb"><div class="bar" style="width:{t['percentage']}%;background:{t['level_color']};animation-delay:{fmt(d + 0.25)}s"></div></div>
    </div>""")

    comp_rows = []
    for i, c in enumerate(complexity):
        d = round(0.2 + i * 0.15, 2)
        comp_rows.append(f"""
    <div class="row" style="animation: slideRow 0.5s ease-out {d}s both;">
      <span class="rl cl">{dot(c['color'])} {c['label']}</span>
      <div class="bt"><div class="bar" style="width:{c['percentage']}%;background:{c['color']};animation-delay:{fmt(d + 0.3)}s"></div></div>
      <span class="rv">{c['percentage']:.0f}%</span>
      <span class="rm">{c['count']} repo{"s" if c['count'] != 1 else ""}</span>
    </div>""")

    active_pct = profile.get("active_pct", 0)
    lang_count = profile.get("languages_count", 0)
    maturity = profile.get("maturity", 0)
    grades = profile.get("grades", [])

    profile_stats = f"""
    <div class="row" style="animation: slideRow 0.5s ease-out 0.2s both;">
      <span class="rl hl">Active</span>
      <div class="bt"><div class="bar" style="width:{active_pct}%;background:#10B981;animation-delay:0.5s"></div></div>
      <span class="rv">{active_pct}%</span>
    </div>
    <div class="row" style="animation: slideRow 0.5s ease-out 0.35s both;">
      <span class="rl hl">Languages</span>
      <span class="pv">{lang_count}</span>
    </div>
    <div class="row" style="animation: slideRow 0.5s ease-out 0.5s both;">
      <span class="rl hl">Maturity</span>
      <span class="pv">{maturity}y</span>
    </div>"""

    grade_badges = []
    for i, g in enumerate(grades):
        d = round(0.3 + i * 0.08, 2)
        grade_badges.append(f"""
    <div class="gb" style="background:{g['color']}15;border-color:{g['color']}44;animation:fadeIn 0.4s ease-out {d}s both;">
      <span class="gl" style="color:{g['color']}">{g['grade']}</span>
      <span class="gln">{g['label']}</span>
    </div>""")

    network_html = ""
    if network:
        parts = []
        for chain in network:
            nodes = []
            for j, node in enumerate(chain):
                nodes.append(
                    f'<span class="nn" style="border-left-color:{node["color"]}">'
                    f'<span class="nnd" style="background:{node["color"]}"></span>'
                    f'<span class="nnn">{node["name"]}</span>'
                    f'<span class="nnp">{node["pct"]}%</span>'
                    f"</span>"
                )
                if j < len(chain) - 1:
                    nodes.append(f'<span class="na" style="color:{node["color"]}66">\u2192</span>')
            parts.append(f'<div class="nc">{"".join(nodes)}</div>')
        network_html = "".join(parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 860" width="100%" height="100%">
  <foreignObject width="100%" height="100%">
    <div xmlns="http://www.w3.org/1999/xhtml" class="card">
      <style>
        :root {{
          --bg1: #0B1121; --bg2: #0F172A;
          --surface: rgba(255,255,255,0.03);
          --border: rgba(255,255,255,0.06);
          --bl: rgba(255,255,255,0.04);
          --text: #F1F5F9; --muted: #64748B;
          --bar-bg: rgba(255,255,255,0.05);
          --shadow: 0 0 0 1px rgba(255,255,255,0.02), 0 8px 32px rgba(0,0,0,0.5);
        }}
        @media (prefers-color-scheme: light) {{
          :root {{
            --bg1: #FFFFFF; --bg2: #F8FAFC;
            --surface: rgba(0,0,0,0.02);
            --border: rgba(0,0,0,0.06);
            --bl: rgba(0,0,0,0.03);
            --text: #0F172A; --muted: #94A3B8;
            --bar-bg: rgba(0,0,0,0.04);
            --shadow: 0 0 0 1px rgba(0,0,0,0.02), 0 8px 32px rgba(0,0,0,0.06);
          }}
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        .card {{
          font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          background: linear-gradient(160deg, var(--bg1), var(--bg2));
          border: 1px solid var(--border);
          border-radius: 20px; padding: 28px;
          box-shadow: var(--shadow);
          width: 100%; min-height: 100%; color: var(--text);
        }}
        h1 {{ font-size: 20px; font-weight: 700; text-align: center; letter-spacing: -0.3px; margin-bottom: 24px; animation: fadeIn 0.6s ease-out both; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .sc {{ background: var(--surface); border: 1px solid var(--bl); border-radius: 14px; padding: 18px; animation: slideUp 0.5s ease-out both; }}
        .sc:nth-child(1) {{ animation-delay: 0.04s; }}
        .sc:nth-child(2) {{ animation-delay: 0.08s; }}
        .sc:nth-child(3) {{ animation-delay: 0.12s; }}
        .sc:nth-child(4) {{ animation-delay: 0.16s; }}
        .sf {{ grid-column: span 2; }}
        h2 {{ font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 12px; }}
        .row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; min-height: 30px; }}
        .rl {{ width: 110px; font-size: 12px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 0; display: flex; align-items: center; gap: 6px; }}
        .cl {{ width: 90px; }}
        .hl {{ width: 80px; }}
        .bt {{ flex: 1; height: 6px; background: var(--bar-bg); border-radius: 3px; overflow: hidden; }}
        .bar {{ height: 100%; border-radius: 3px; animation: grow 0.8s cubic-bezier(0.16, 1, 0.3, 1) both; }}
        .rv {{ width: 36px; font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; flex-shrink: 0; text-align: right; }}
        .rm {{ font-size: 10px; color: var(--muted); flex-shrink: 0; width: 48px; }}
        .pv {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; color: var(--text); }}
        .tg {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .tc {{ background: var(--bar-bg); border: 1px solid var(--bl); border-radius: 10px; padding: 14px 8px 10px; display: flex; flex-direction: column; align-items: center; gap: 3px; position: relative; overflow: hidden; }}
        .tca {{ position: absolute; top: 0; left: 0; right: 0; height: 3px; }}
        .tcn {{ font-size: 12px; font-weight: 600; margin-top: 2px; }}
        .tcl {{ font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; }}
        .tcb {{ width: 100%; height: 3px; background: var(--bar-bg); border-radius: 2px; overflow: hidden; margin-top: 3px; }}
        .gg {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; }}
        .gb {{ display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 8px 4px; border: 1px solid; border-radius: 10px; }}
        .gl {{ font-size: 18px; font-weight: 800; letter-spacing: -0.5px; line-height: 1; }}
        .gln {{ font-size: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; color: var(--muted); }}
        .nc {{ display: flex; align-items: center; justify-content: center; gap: 4px; margin-bottom: 8px; flex-wrap: wrap; }}
        .nc:last-child {{ margin-bottom: 0; }}
        .nn {{ display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px 5px 8px; border: 1px solid var(--bl); border-left: 3px solid; border-radius: 8px; background: var(--bar-bg); font-size: 11px; animation: fadeIn 0.4s ease-out both; }}
        .nnd {{ display: inline-block; width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }}
        .nnn {{ font-weight: 600; }}
        .nnp {{ font-size: 10px; opacity: 0.5; }}
        .na {{ font-size: 14px; margin: 0 2px; animation: fadeIn 0.3s ease-out both; }}
        .footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 18px; padding-top: 12px; border-top: 1px solid var(--bl); font-size: 10px; color: var(--muted); animation: fadeIn 0.6s ease-out 0.6s both; }}
        @keyframes grow {{ from {{ width: 0%; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes slideRow {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: translateX(0); }} }}
        @media (max-width: 500px) {{
          .grid {{ grid-template-columns: 1fr; }}
          .sf {{ grid-column: span 1; }}
          .tg {{ grid-template-columns: repeat(2, 1fr); }}
          .rl {{ width: 80px; }}
          .rm {{ display: none; }}
          .hl {{ width: 70px; }}
        }}
      </style>
      <h1>Profile Analytics</h1>
      <div class="grid">
        <div class="sc sf">
          <h2>Core Technologies</h2>
          <div class="tg">{"".join(tech_cards)}</div>
        </div>
        <div class="sc">
          <h2>Project Complexity</h2>
          {"".join(comp_rows)}
        </div>
        <div class="sc">
          <h2>Code Profile</h2>
          {profile_stats}
          <div class="gg">{"".join(grade_badges)}</div>
        </div>
        <div class="sc sf">
          <h2>Stack</h2>
          {network_html}
        </div>
      </div>
      <div style="height:20px"></div>
      <div class="footer">
        <span>Updated {generated}</span>
        <span>GitHub Actions \u00b7 profile-analytics</span>
      </div>
    </div>
  </foreignObject>
</svg>'''
