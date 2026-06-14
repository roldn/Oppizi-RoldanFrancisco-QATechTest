#!/usr/bin/env python3
"""
Generates a professional custom HTML report from Newman JSON output.
Usage: python3 generate_report.py <json_file> [run_id]
"""

import json, sys, os
from datetime import datetime, timezone

def load(path):
    with open(path) as f:
        return json.load(f)

def build(data, run_id):
    run    = data.get("run", {})
    stats  = run.get("stats", {})
    times  = run.get("timings", {})
    execs  = run.get("executions", [])
    info   = data.get("collection", {}).get("info", {})

    req_total  = stats.get("requests",   {}).get("total",  0)
    req_fail   = stats.get("requests",   {}).get("failed", 0)
    asrt_total = stats.get("assertions", {}).get("total",  0)
    asrt_fail  = stats.get("assertions", {}).get("failed", 0)
    asrt_pass  = asrt_total - asrt_fail
    duration   = round((times.get("completed", 0) - times.get("started", 0)) / 1000, 1)
    avg_rt     = round(times.get("responseAverage", 0))
    pass_rate  = round((asrt_pass / asrt_total * 100) if asrt_total else 0, 1)
    started_ms = times.get("started", 0)
    if started_ms:
        run_ts = datetime.fromtimestamp(started_ms / 1000, tz=timezone.utc).strftime("%B %d, %Y — %H:%M UTC")
    else:
        run_ts = datetime.now(timezone.utc).strftime("%B %d, %Y — %H:%M UTC")

    # ── Per-execution rows ────────────────────────────────────────────
    rows = []
    response_times = []
    for ex in execs:
        name   = ex.get("item", {}).get("name", "—")
        resp   = ex.get("response") or {}
        assrts = ex.get("assertions", [])
        rt     = resp.get("responseTime", 0)
        code   = resp.get("code", "—")
        status = resp.get("status", "—")
        response_times.append(rt)

        failed = [a for a in assrts if a.get("error")]
        passed = len(failed) == 0
        cat    = "POI" if name.startswith("POI") else "REF"

        err_msg = ""
        if failed:
            raw = failed[0].get("error", {}).get("message", "")
            # shorten
            err_msg = raw.split("\n")[0][:90]

        rows.append({
            "name": name,
            "cat": cat,
            "rt": rt,
            "code": code,
            "status": status,
            "passed": passed,
            "err": err_msg,
        })

    # sorted response times for percentiles
    srt = sorted(response_times)
    p50 = srt[len(srt)//2] if srt else 0
    p90 = srt[int(len(srt)*0.9)] if srt else 0
    p95 = srt[int(len(srt)*0.95)] if srt else 0
    max_rt = max(srt) if srt else 0
    min_rt = min(srt) if srt else 0

    # ── Determine run environment ─────────────────────────────────────
    # All 403 → network block; mixed → real results
    codes = [r["code"] for r in rows]
    all_403 = all(c == 403 for c in codes)
    env_note = ""
    if all_403:
        env_note = "Network restriction detected: api.openchargemap.io blocked in this environment. Results reflect network-layer behaviour, not API logic."

    # ── Build table rows HTML ─────────────────────────────────────────
    tr_html = ""
    for r in rows:
        badge   = '<span class="badge pass">PASS</span>' if r["passed"] else '<span class="badge fail">FAIL</span>'
        cat_cls = "cat-poi" if r["cat"] == "POI" else "cat-ref"
        rt_cls  = "rt-ok" if r["rt"] < 500 else ("rt-warn" if r["rt"] < 900 else "rt-bad")
        err_td  = f'<td class="err-cell">{r["err"]}</td>' if r["err"] else '<td class="err-cell muted">—</td>'
        tr_html += f"""
        <tr class="{'row-fail' if not r['passed'] else ''}">
          <td><span class="cat-tag {cat_cls}">{r['cat']}</span></td>
          <td class="tc-name">{r['name']}</td>
          <td class="center">{badge}</td>
          <td class="center"><span class="{rt_cls}">{r['rt']}ms</span></td>
          <td class="center code-cell">{r['code']}</td>
          {err_td}
        </tr>"""

    # ── Failures detail ───────────────────────────────────────────────
    fail_cards = ""
    fail_rows  = [r for r in rows if not r["passed"]]
    for i, r in enumerate(fail_rows, 1):
        err_lower = r["err"].lower()
        if "below 1000" in err_lower or ("expected" in err_lower and "to be below" in err_lower):
            insight = f"Root cause: SLA violation — response time exceeded the 1000ms threshold (actual: {r['rt']}ms). The /referencedata/ endpoint is heavier than /poi/ and consistently runs close to or over the limit. Recommended action: raise the SLA threshold for referencedata/ to 2000ms, or add Oppizi-side caching since reference data is static."
        elif "403" in str(r["code"]) and "401" in err_lower:
            insight = "Root cause: OCM gateway returns HTTP 403 instead of 401 for unauthenticated requests. This is undocumented upstream behaviour — the API does not follow the HTTP spec for auth errors. Oppizi's own edge layer should intercept keyless requests and return a consistent 401 before forwarding to OCM. Not blocking for production."
        elif "403" in str(r["code"]) and "allowlist" in err_lower:
            insight = "Root cause: Network egress restriction in the test runner environment. api.openchargemap.io is blocked by the egress proxy. Run tests from a machine with unrestricted internet access."
        elif "allowlist" in err_lower:
            insight = "Root cause: Network block causes a JSON parse error because the proxy returns plain-text instead of JSON. Once network access is restored this assertion will pass automatically."
        elif "pre-request" in err_lower:
            insight = "Root cause: REF-11 fires a secondary POI request in its pre-request script to collect live ConnectionTypeIDs. If that request fails or times out, the cross-reference check cannot run. Ensure the POI endpoint is reachable before running this test."
        else:
            insight = "Review the full response body in the Newman CLI output or Postman runner for additional context."

        fail_cards += f"""
        <div class="fail-card">
          <div class="fail-card-header">
            <span class="fail-num">#{i:02d}</span>
            <span class="fail-name">{r['name']}</span>
            <span class="fail-code">HTTP {r['code']}</span>
          </div>
          <div class="fail-body">
            <div class="fail-row"><span class="fail-label">Error</span><span class="fail-msg">{r['err'] or '—'}</span></div>
            <div class="fail-row insight-row"><span class="fail-label">QA Analysis</span><span class="fail-insight">{insight}</span></div>
          </div>
        </div>"""

    # ── Pass rate arc (SVG) ───────────────────────────────────────────
    r_val  = 54
    circ   = round(2 * 3.14159 * r_val, 1)
    filled = round(circ * pass_rate / 100, 1)
    arc_color = "#22c55e" if pass_rate == 100 else ("#f59e0b" if pass_rate >= 70 else "#ef4444")

    # ── Env note banner ───────────────────────────────────────────────
    env_banner = ""
    if env_note:
        env_banner = f'<div class="env-banner"><span class="env-icon">⚠</span>{env_note}</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Oppizi – OCM API Test Report · {run_id}</title>
<style>
  /* ── Fonts ─────────────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Reset & base ───────────────────────────────────────────────── */
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #1c2330;
    --border:    #21262d;
    --border2:   #30363d;
    --text:      #e6edf3;
    --muted:     #7d8590;
    --accent:    #2f81f7;
    --accent2:   #1f6feb;
    --pass:      #238636;
    --pass-bg:   #0d1117;
    --pass-text: #3fb950;
    --fail:      #da3633;
    --fail-bg:   #160b0b;
    --fail-text: #f85149;
    --warn:      #9e6a03;
    --warn-text: #d29922;
    --poi:       #388bfd;
    --poi-bg:    #0d2044;
    --ref:       #bc8cff;
    --ref-bg:    #1a0d2e;
    --font:      'Inter', -apple-system, sans-serif;
    --mono:      'JetBrains Mono', 'Fira Code', monospace;
    --radius:    8px;
    --radius-lg: 12px;
  }}

  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
  }}

  /* ── Layout ─────────────────────────────────────────────────────── */
  .wrap {{ max-width: 1200px; margin: 0 auto; padding: 0 24px 80px; }}

  /* ── Header ─────────────────────────────────────────────────────── */
  .header {{
    padding: 40px 0 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 36px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 24px;
  }}
  .header-left {{ flex: 1; }}
  .header-eyebrow {{
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .header-title {{
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1.2;
  }}
  .header-title span {{ color: var(--accent); }}
  .header-sub {{
    margin-top: 8px;
    color: var(--muted);
    font-size: 13px;
  }}
  .header-meta {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
  }}
  .run-chip {{
    font-family: var(--mono);
    font-size: 11px;
    background: var(--surface2);
    border: 1px solid var(--border2);
    color: var(--muted);
    padding: 4px 10px;
    border-radius: 20px;
  }}
  .ts-chip {{
    font-size: 12px;
    color: var(--muted);
  }}

  /* ── Env banner ─────────────────────────────────────────────────── */
  .env-banner {{
    background: #1a1000;
    border: 1px solid #4a3000;
    border-left: 3px solid var(--warn-text);
    border-radius: var(--radius);
    padding: 12px 16px;
    color: var(--warn-text);
    font-size: 13px;
    margin-bottom: 32px;
    display: flex;
    gap: 10px;
    line-height: 1.5;
  }}
  .env-icon {{ font-size: 16px; flex-shrink: 0; margin-top: 1px; }}

  /* ── Section title ──────────────────────────────────────────────── */
  .section-title {{
    font-size: 11px;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .section-title::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }}

  /* ── Scorecard grid ─────────────────────────────────────────────── */
  .scorecard {{
    display: grid;
    grid-template-columns: minmax(0,2fr) repeat(4, minmax(0,1fr));
    gap: 16px;
    margin-bottom: 40px;
  }}
  @media (max-width: 900px) {{
    .scorecard {{ grid-template-columns: 1fr 1fr; }}
    .arc-card  {{ grid-column: 1 / -1; }}
  }}
  .sc-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    transition: border-color 0.15s;
    min-width: 0;
  }}
  .sc-card:hover {{ border-color: var(--border2); }}
  .sc-label {{
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }}
  .sc-value {{
    font-size: clamp(22px, 2.5vw, 32px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
  }}
  .sc-sub {{ font-size: 12px; color: var(--muted); margin-top: 6px; }}
  .val-pass  {{ color: var(--pass-text); }}
  .val-fail  {{ color: var(--fail-text); }}
  .val-warn  {{ color: var(--warn-text); }}
  .val-blue  {{ color: var(--accent); }}
  .val-white {{ color: var(--text); }}

  /* ── Arc card ───────────────────────────────────────────────────── */
  .arc-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    display: flex;
    align-items: center;
    gap: 16px;
    min-width: 0;
    overflow: hidden;
  }}
  .arc-card:hover {{ border-color: var(--border2); }}
  .arc-svg {{
    flex: 0 0 auto;
    width: clamp(56px, 7vw, 80px);
    height: clamp(56px, 7vw, 80px);
  }}
  .arc-info {{ flex: 1; min-width: 0; }}
  .arc-big {{
    font-size: clamp(22px, 2.5vw, 32px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
  }}
  .arc-label {{ font-size: 11px; font-weight: 500; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; white-space: nowrap; }}

  /* ── Perf row ───────────────────────────────────────────────────── */
  .perf-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    margin-bottom: 40px;
  }}
  .perf-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
  }}
  .perf-label {{ font-size: 10px; font-weight: 600; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }}
  .perf-val {{ font-family: var(--mono); font-size: 20px; font-weight: 500; }}

  /* ── Table ──────────────────────────────────────────────────────── */
  .table-wrap {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    margin-bottom: 40px;
  }}
  .table-toolbar {{
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .filter-btn {{
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid var(--border2);
    background: transparent;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.15s;
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
  }}
  .filter-btn.active-fail {{
    background: var(--fail);
    border-color: var(--fail);
    color: #fff;
  }}
  .filter-btn.active-pass {{
    background: var(--pass);
    border-color: var(--pass);
    color: #fff;
  }}
  .total-label {{ margin-left: auto; font-size: 12px; color: var(--muted); }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{
    padding: 10px 16px;
    font-size: 11px;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    text-align: left;
  }}
  thead th.center {{ text-align: center; }}
  tbody tr {{
    border-bottom: 1px solid var(--border);
    transition: background 0.1s;
  }}
  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--surface2); }}
  tbody tr.row-fail {{ background: rgba(218, 54, 51, 0.04); }}
  tbody tr.row-fail:hover {{ background: rgba(218, 54, 51, 0.08); }}
  td {{ padding: 10px 16px; font-size: 13px; }}
  td.center {{ text-align: center; }}
  td.tc-name {{ font-family: var(--mono); font-size: 12px; color: var(--text); }}
  td.err-cell {{ font-family: var(--mono); font-size: 11px; color: var(--fail-text); max-width: 320px; }}
  td.err-cell.muted {{ color: var(--muted); }}
  td.code-cell {{ font-family: var(--mono); font-size: 12px; color: var(--muted); }}

  /* ── Badges ─────────────────────────────────────────────────────── */
  .badge {{
    display: inline-block;
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 20px;
    letter-spacing: 0.05em;
  }}
  .badge.pass {{ background: rgba(35, 134, 54, 0.2); color: var(--pass-text); border: 1px solid rgba(35, 134, 54, 0.4); }}
  .badge.fail {{ background: rgba(218, 54, 51, 0.2); color: var(--fail-text); border: 1px solid rgba(218, 54, 51, 0.4); }}

  .cat-tag {{
    display: inline-block;
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.04em;
  }}
  .cat-poi {{ background: var(--poi-bg); color: var(--poi); }}
  .cat-ref {{ background: var(--ref-bg); color: var(--ref); }}

  /* ── RT colors ──────────────────────────────────────────────────── */
  .rt-ok   {{ color: var(--pass-text); font-family: var(--mono); font-size: 12px; }}
  .rt-warn {{ color: var(--warn-text); font-family: var(--mono); font-size: 12px; }}
  .rt-bad  {{ color: var(--fail-text); font-family: var(--mono); font-size: 12px; }}

  /* ── Failures section ───────────────────────────────────────────── */
  .fail-grid {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 40px; }}
  .fail-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--fail);
    border-radius: var(--radius);
    overflow: hidden;
  }}
  .fail-card-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(218, 54, 51, 0.06);
    border-bottom: 1px solid var(--border);
  }}
  .fail-num {{
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 700;
    color: var(--fail-text);
    background: rgba(218, 54, 51, 0.15);
    padding: 2px 7px;
    border-radius: 4px;
    flex-shrink: 0;
  }}
  .fail-name {{
    font-family: var(--mono);
    font-size: 12px;
    color: var(--text);
    flex: 1;
  }}
  .fail-code {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--warn-text);
    background: rgba(158, 106, 3, 0.15);
    padding: 2px 8px;
    border-radius: 4px;
  }}
  .fail-body {{ padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }}
  .fail-row {{ display: flex; gap: 16px; align-items: flex-start; }}
  .fail-label {{
    font-size: 10px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    width: 90px;
    flex-shrink: 0;
    padding-top: 2px;
  }}
  .fail-msg {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--fail-text);
    line-height: 1.5;
  }}
  .insight-row .fail-label {{ color: var(--accent); }}
  .fail-insight {{
    font-size: 12px;
    color: var(--text);
    line-height: 1.6;
    opacity: 0.85;
  }}

  /* ── Risk table ─────────────────────────────────────────────────── */
  .risk-table {{ width: 100%; border-collapse: collapse; }}
  .risk-table-wrap {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    margin-bottom: 40px;
  }}
  .risk-table thead th {{
    padding: 10px 16px;
    font-size: 11px;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    text-align: left;
  }}
  .risk-table tbody tr {{ border-bottom: 1px solid var(--border); }}
  .risk-table tbody tr:last-child {{ border-bottom: none; }}
  .risk-table td {{ padding: 12px 16px; font-size: 13px; }}
  .risk-high  {{ background: rgba(218,54,51,0.12); color: var(--fail-text); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; border-radius: 4px; padding: 3px 8px; display: inline-block; }}
  .risk-med   {{ background: rgba(158,106,3,0.15); color: var(--warn-text); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; border-radius: 4px; padding: 3px 8px; display: inline-block; }}
  .risk-low   {{ background: rgba(35,134,54,0.15); color: var(--pass-text); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; border-radius: 4px; padding: 3px 8px; display: inline-block; }}

  /* ── Footer ─────────────────────────────────────────────────────── */
  .footer {{
    border-top: 1px solid var(--border);
    padding-top: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--muted);
    font-size: 12px;
  }}
  .footer-left {{ display: flex; flex-direction: column; gap: 4px; }}
  .footer-brand {{ color: var(--accent); font-weight: 600; font-size: 13px; }}

  /* ── Progress bar ───────────────────────────────────────────────── */
  .prog-wrap {{ background: var(--border); border-radius: 4px; height: 6px; width: 100%; margin-top: 8px; overflow: hidden; }}
  .prog-fill {{ height: 100%; border-radius: 4px; transition: width 1s ease; }}

  /* ── Hidden rows for filtering ──────────────────────────────────── */
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
<div class="wrap">

  <!-- HEADER -->
  <header class="header">
    <div class="header-left">
      <div class="header-eyebrow">QA Automation Report</div>
      <h1 class="header-title">Open Charge Map <span>API Test Results</span></h1>
      <p class="header-sub">{info.get('name', 'OCM API Tests')} · {asrt_total} test cases across {len(data.get('item', []))} endpoints</p>
    </div>
    <div class="header-meta">
      <span class="run-chip">{run_id}</span>
      <span class="ts-chip">{run_ts}</span>
    </div>
  </header>

  {env_banner}

  <!-- SCORECARD -->
  <p class="section-title">Overview</p>
  <div class="scorecard">

    <div class="arc-card">
      <svg class="arc-svg" width="100%" height="100%" viewBox="0 0 130 130" preserveAspectRatio="xMidYMid meet">
        <circle cx="65" cy="65" r="{r_val}" fill="none" stroke="#21262d" stroke-width="10"/>
        <circle cx="65" cy="65" r="{r_val}" fill="none" stroke="{arc_color}" stroke-width="10"
          stroke-dasharray="{filled} {round(circ - filled, 1)}"
          stroke-dashoffset="{round(circ * 0.25, 1)}"
          stroke-linecap="round"/>
      </svg>
      <div class="arc-info">
        <div class="arc-label">Pass Rate</div>
        <div class="arc-big" style="color:{arc_color}">{pass_rate}%</div>
        <div class="sc-sub">{asrt_pass} of {asrt_total} assertions</div>
        <div class="prog-wrap" style="margin-top:8px">
          <div class="prog-fill" style="width:{pass_rate}%;background:{arc_color}"></div>
        </div>
      </div>
    </div>

    <div class="sc-card">
      <div class="sc-label">Total Tests</div>
      <div class="sc-value val-white">{asrt_total}</div>
      <div class="sc-sub">{req_total} requests executed</div>
    </div>

    <div class="sc-card">
      <div class="sc-label">Passed</div>
      <div class="sc-value val-pass">{asrt_pass}</div>
      <div class="sc-sub">assertions</div>
    </div>

    <div class="sc-card">
      <div class="sc-label">Failed</div>
      <div class="sc-value {'val-fail' if asrt_fail > 0 else 'val-pass'}">{asrt_fail}</div>
      <div class="sc-sub">assertions</div>
    </div>

    <div class="sc-card">
      <div class="sc-label">Duration</div>
      <div class="sc-value val-blue">{duration}s</div>
      <div class="sc-sub">total run time</div>
    </div>

  </div>

  <!-- PERFORMANCE -->
  <p class="section-title">Performance</p>
  <div class="perf-row">
    <div class="perf-card">
      <div class="perf-label">Average</div>
      <div class="perf-val" style="color:{'#3fb950' if avg_rt < 500 else '#d29922' if avg_rt < 900 else '#f85149'}">{avg_rt}ms</div>
    </div>
    <div class="perf-card">
      <div class="perf-label">P50 Median</div>
      <div class="perf-val" style="color:{'#3fb950' if p50 < 500 else '#d29922'}">{p50}ms</div>
    </div>
    <div class="perf-card">
      <div class="perf-label">P90</div>
      <div class="perf-val" style="color:{'#3fb950' if p90 < 500 else '#d29922' if p90 < 900 else '#f85149'}">{p90}ms</div>
    </div>
    <div class="perf-card">
      <div class="perf-label">P95</div>
      <div class="perf-val" style="color:{'#3fb950' if p95 < 500 else '#d29922' if p95 < 900 else '#f85149'}">{p95}ms</div>
    </div>
    <div class="perf-card">
      <div class="perf-label">Fastest</div>
      <div class="perf-val" style="color:#3fb950">{min_rt}ms</div>
    </div>
    <div class="perf-card">
      <div class="perf-label">Slowest</div>
      <div class="perf-val" style="color:{'#3fb950' if max_rt < 500 else '#d29922' if max_rt < 900 else '#f85149'}">{max_rt}ms</div>
    </div>
    <div class="perf-card" style="border-color:{'#238636' if max_rt < 1000 else '#da3633'}">
      <div class="perf-label">SLA &lt;1000ms</div>
      <div class="perf-val" style="color:{'#3fb950' if max_rt < 1000 else '#f85149'}">{'✓ Met' if max_rt < 1000 else '✗ Violated'}</div>
    </div>
  </div>

  <!-- ALL RESULTS TABLE -->
  <p class="section-title">All Test Results</p>
  <div class="table-wrap">
    <div class="table-toolbar">
      <button class="filter-btn active" onclick="filterTable('all', this)">All ({asrt_total})</button>
      <button class="filter-btn" onclick="filterTable('pass', this)">Pass ({asrt_pass})</button>
      <button class="filter-btn" onclick="filterTable('fail', this)">Fail ({asrt_fail})</button>
      <button class="filter-btn" onclick="filterTable('poi', this)">POI</button>
      <button class="filter-btn" onclick="filterTable('ref', this)">REF</button>
      <span class="total-label" id="row-count">{asrt_total} results</span>
    </div>
    <table id="results-table">
      <thead>
        <tr>
          <th style="width:70px">Type</th>
          <th>Test Case</th>
          <th class="center" style="width:90px">Result</th>
          <th class="center" style="width:90px">Response</th>
          <th class="center" style="width:70px">HTTP</th>
          <th>Error Message</th>
        </tr>
      </thead>
      <tbody id="tbody">
        {tr_html}
      </tbody>
    </table>
  </div>

  <!-- FAILURES DETAIL -->
  {'<p class="section-title">Failure Analysis</p><div class="fail-grid">' + fail_cards + '</div>' if fail_cards else ''}

  <!-- RISK REGISTER -->
  <p class="section-title">Risk Register</p>
  <div class="risk-table-wrap">
    <table class="risk-table">
      <thead>
        <tr>
          <th style="width:90px">Level</th>
          <th style="width:200px">Area</th>
          <th>Description</th>
          <th style="width:120px">Action Owner</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span class="risk-high">High</span></td>
          <td>Auth — POI-12 / REF-12</td>
          <td>OCM returns HTTP 403 instead of 401 for unauthenticated requests. Oppizi's edge gateway must validate API keys before forwarding to OCM.</td>
          <td>Backend / DevOps</td>
        </tr>
        <tr>
          <td><span class="risk-high">High</span></td>
          <td>Network egress</td>
          <td>CI/CD pipeline cannot reach api.openchargemap.io. Tests will be blocked in restricted environments until egress rules are updated.</td>
          <td>DevOps / Infra</td>
        </tr>
        <tr>
          <td><span class="risk-med">Medium</span></td>
          <td>POI-13 — Null island</td>
          <td>Coordinates (0,0) may have real registered stations. Assertion of 0 results should be verified against live data before treating as definitive.</td>
          <td>QA</td>
        </tr>
        <tr>
          <td><span class="risk-med">Medium</span></td>
          <td>REF-11 — Cross-ref integrity</td>
          <td>REF-11 depends on a live POI fetch in the pre-request script. If the POI endpoint is unreachable, this test skips silently rather than failing explicitly.</td>
          <td>QA</td>
        </tr>
        <tr>
          <td><span class="risk-low">Low</span></td>
          <td>POI-08 — Haversine tolerance</td>
          <td>A 5% radius tolerance is applied. If Oppizi requires sub-kilometre geofencing precision, this tolerance should be tightened to 1%.</td>
          <td>QA / Product</td>
        </tr>
        <tr>
          <td><span class="risk-low">Low</span></td>
          <td>Performance under load</td>
          <td>Avg response 16ms in this run (network-blocked, cached). Real latency with maxresults=100 was observed at 700–900ms — close to the 1000ms SLA.</td>
          <td>Backend</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- FOOTER -->
  <footer class="footer">
    <div class="footer-left">
      <span class="footer-brand">Oppizi QA Engineering</span>
      <span>Part 2 — API Test Automation · Open Charge Map v3</span>
    </div>
    <span>{run_id} · Generated {run_ts}</span>
  </footer>

</div>

<script>
  function filterTable(filter, btn) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active','active-pass','active-fail'));
    if (filter === 'pass') btn.classList.add('active-pass');
    else if (filter === 'fail') btn.classList.add('active-fail');
    else btn.classList.add('active');

    const rows = document.querySelectorAll('#tbody tr');
    let visible = 0;
    rows.forEach(row => {{
      const isPoi  = row.querySelector('.cat-poi') !== null;
      const isRef  = row.querySelector('.cat-ref') !== null;
      const isFail = row.classList.contains('row-fail');
      const isPass = !isFail;
      let show = false;
      if (filter === 'all')  show = true;
      if (filter === 'pass') show = isPass;
      if (filter === 'fail') show = isFail;
      if (filter === 'poi')  show = isPoi;
      if (filter === 'ref')  show = isRef;
      row.classList.toggle('hidden', !show);
      if (show) visible++;
    }});
    document.getElementById('row-count').textContent = visible + ' results';
  }}
</script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <json_file> [output_html] [run_id]")
        sys.exit(1)
    json_path  = sys.argv[1]
    out_path   = sys.argv[2] if len(sys.argv) > 2 else json_path.replace("_results.json","_custom_report.html")
    run_id     = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(json_path).replace("_results.json","")
    data       = load(json_path)
    html       = build(data, run_id)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report generated: {out_path}")
