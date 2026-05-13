#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""Generate the LATTICE capability landscape HTML report.

Single self-contained HTML file with embedded JSON data and Plotly from CDN.
Mirrors the pattern from meta/harness/benchy/LATTICE_BENCH_REPORT.html — drag
anywhere, works offline once Plotly is cached. Updates on every re-run.

Output:
    meta/harness/LATTICE_CAPABILITY_LANDSCAPE.html

Usage:
    uv run scripts/generate-capability-landscape.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from registry_parser import parse_registries, summary  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "meta" / "harness" / "LATTICE_CAPABILITY_LANDSCAPE.html"


def slim_rows(rows):
    """Strip heavy fields before embedding in HTML — keep only what the UI needs."""
    out = []
    for r in rows:
        out.append({
            "registry": r["registry"],
            "registry_path": r["registry_path"],
            "tool": r["tool"],
            "id": r["id"],
            "surface": r["surface"],
            "name": r["name"],
            "state": r["state"],
            "description": (r["description"] or "")[:240],
            "reason": r.get("reason"),
            "target_phase": r.get("target_phase"),
            "blocker": r.get("blocker"),
            "n_install_evidence": len(r.get("install_evidence_paths") or []),
            "n_static_present": len(r.get("static_paths_present") or []),
            "n_advisory_stale": len(r.get("static_paths_advisory_stale") or []),
            "advisory_stale_paths": r.get("static_paths_advisory_stale") or [],
            "install_evidence_paths": r.get("install_evidence_paths") or [],
        })
    return out


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>LATTICE Capability Landscape — __GENERATED_AT__</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body {
    font-family: ui-monospace, "SF Mono", Monaco, Menlo, Consolas, monospace;
    background: #0a0a0a; color: #e5e5e5;
    margin: 0; padding: 24px;
    line-height: 1.5;
    font-size: 13px;
  }
  h1 { font-size: 18px; margin: 0 0 4px; letter-spacing: 0.02em; }
  h2 { font-size: 14px; margin: 32px 0 8px; color: #fbbf24; letter-spacing: 0.04em; text-transform: uppercase; font-weight: 600; }
  .meta { color: #888; margin-bottom: 24px; font-size: 11px; }
  .stats {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px; margin: 16px 0 32px;
  }
  .stat {
    background: #131313; border: 1px solid #2a2a2a;
    padding: 12px 16px; border-radius: 6px;
  }
  .stat .k { color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat .v { font-size: 22px; font-weight: 600; margin-top: 4px; }
  .stat .v.active { color: #6ee7b7; }
  .stat .v.deferred { color: #fbbf24; }
  .stat .v.blocked { color: #fca5a5; }
  .stat .v.advisory { color: #fca5a5; }
  .panel {
    background: #131313; border: 1px solid #2a2a2a;
    border-radius: 6px; padding: 16px; margin: 16px 0;
  }
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 1000px) { .charts { grid-template-columns: 1fr; } }
  .chart { background: #131313; border: 1px solid #2a2a2a; border-radius: 6px; padding: 8px; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }
  th, td { padding: 6px 10px; text-align: left; border-bottom: 1px solid #1f1f1f; }
  th { color: #fbbf24; font-weight: 600; cursor: pointer; user-select: none; position: sticky; top: 0; background: #131313; }
  th:hover { color: #fde68a; }
  tr:hover td { background: #181818; }
  .badge {
    display: inline-block; padding: 1px 7px; border-radius: 3px;
    font-size: 10px; letter-spacing: 0.03em; text-transform: uppercase;
    border: 1px solid;
  }
  .badge.ACTIVE { background: #053b1f; border-color: #1e7a3e; color: #6ee7b7; }
  .badge.DEFERRED { background: #3b2c05; border-color: #7a5d1e; color: #fbbf24; }
  .badge.BLOCKED { background: #3b0808; border-color: #7a1e1e; color: #fca5a5; }
  .badge.stale { background: #1a1a1a; border-color: #5a1e1e; color: #fca5a5; margin-left: 6px; font-size: 9px; }
  .badge.install { background: #131319; border-color: #1e3a7a; color: #93c5fd; margin-left: 6px; font-size: 9px; }
  input[type="search"], select {
    background: #131313; color: #e5e5e5;
    border: 1px solid #2a2a2a; border-radius: 4px;
    padding: 6px 10px; font-family: inherit; font-size: 12px;
    margin-right: 8px;
  }
  .stale-list { font-size: 11px; color: #888; margin-top: 4px; }
  .stale-list code { background: #1a1a1a; padding: 1px 4px; border-radius: 3px; color: #fca5a5; }
  .legend-note { font-size: 11px; color: #888; margin: 8px 0 16px; }
  .footer { margin-top: 48px; color: #555; font-size: 10px; text-align: center; }
  a { color: #93c5fd; }
</style>
</head>
<body>

<h1>LATTICE Capability Landscape</h1>
<div class="meta">Generated __GENERATED_AT__ from <code>analysis/capabilities/*-capability-registry.yaml</code> by <code>scripts/generate-capability-landscape.py</code>. The matrix is the trust gate.</div>

<div class="stats" id="stats"></div>

<h2>Distributions</h2>
<div class="legend-note">
  <b>ACTIVE</b> — wired into LATTICE with proof artifact.&nbsp;
  <b>DEFERRED</b> — deliberate hold with curated reason + target phase.&nbsp;
  <b>BLOCKED</b> — external blocker with resolution path.&nbsp;
  <b style="color:#fca5a5">advisory-stale</b> — ACTIVE row claims an in-repo path that the parser cannot verify on disk; may be branch-conditional, aspirational, or legitimately stale. <b>Not a failure.</b> Human review decides.
</div>

<div class="charts">
  <div class="chart" id="state-pie"></div>
  <div class="chart" id="surface-bar"></div>
</div>
<div class="panel" id="registry-bar-panel"><div id="registry-bar"></div></div>

<h2>Advisory-stale rows — review when convenient</h2>
<div class="legend-note">Below: ACTIVE rows whose <code>wired_at</code> or <code>proof.evidence</code> entries name in-repo paths that don't currently exist on disk. Three causes: (1) branch-conditional (file lands when a sibling PR merges), (2) aspirational (the capability is real upstream but not LATTICE-wired yet), (3) legitimately stale. Choose row-by-row.</div>
<div id="advisory-stale-panel" class="panel"></div>

<h2>All capability rows</h2>
<div class="legend-note">Filter by registry, state, or search by id/name/description. Click any column header to sort. Rows with the <span class="badge stale">stale</span> badge have unverifiable paths; rows with the <span class="badge install">install</span> badge claim outside-repo install evidence (parser-correctly skipped).</div>

<div style="margin-bottom: 8px;">
  <input type="search" id="filter-q" placeholder="Search id / name / description..." style="min-width: 280px;" />
  <select id="filter-state">
    <option value="">all states</option>
    <option value="ACTIVE">ACTIVE</option>
    <option value="DEFERRED">DEFERRED</option>
    <option value="BLOCKED">BLOCKED</option>
  </select>
  <select id="filter-registry">
    <option value="">all registries</option>
  </select>
  <select id="filter-surface">
    <option value="">all surfaces</option>
  </select>
  <span id="row-count" style="color:#888; margin-left:12px;"></span>
</div>

<div class="panel" style="padding:0; max-height: 600px; overflow:auto;">
  <table id="rows-table">
    <thead>
      <tr>
        <th data-col="registry">Registry</th>
        <th data-col="state">State</th>
        <th data-col="surface">Surface</th>
        <th data-col="id">ID</th>
        <th data-col="name">Name</th>
        <th data-col="description">Description</th>
      </tr>
    </thead>
    <tbody id="rows-tbody"></tbody>
  </table>
</div>

<div class="footer">LATTICE Meta-Harness · capability landscape · __GENERATED_AT__</div>

<script>
const DATA = __EMBED_DATA__;

const ROWS = DATA.rows;
const SUMMARY = DATA.summary;

// ──────────────────────────────────────────────────────────────────────────
// Stats cards
// ──────────────────────────────────────────────────────────────────────────
function renderStats() {
  const stats = [
    {k: "Rows total", v: SUMMARY.total_rows, cls: ""},
    {k: "Registries", v: Object.keys(SUMMARY.by_registry).length, cls: ""},
    {k: "ACTIVE", v: SUMMARY.by_state.ACTIVE || 0, cls: "active"},
    {k: "DEFERRED", v: SUMMARY.by_state.DEFERRED || 0, cls: "deferred"},
    {k: "BLOCKED", v: SUMMARY.by_state.BLOCKED || 0, cls: "blocked"},
    {k: "Advisory-stale", v: SUMMARY.advisory_stale_rows.length, cls: "advisory"},
  ];
  document.getElementById("stats").innerHTML = stats.map(s =>
    `<div class="stat"><div class="k">${s.k}</div><div class="v ${s.cls}">${s.v}</div></div>`
  ).join("");
}

// ──────────────────────────────────────────────────────────────────────────
// Plotly: state donut
// ──────────────────────────────────────────────────────────────────────────
function renderStatePie() {
  const labels = ["ACTIVE", "DEFERRED", "BLOCKED"];
  const values = labels.map(l => SUMMARY.by_state[l] || 0);
  const colors = ["#1e7a3e", "#7a5d1e", "#7a1e1e"];
  Plotly.newPlot("state-pie", [{
    type: "pie", hole: 0.55,
    labels, values, marker: {colors},
    textfont: {color: "#e5e5e5"},
    hovertemplate: "%{label}: %{value} (%{percent})<extra></extra>",
  }], {
    title: {text: "State distribution", font: {color: "#fbbf24", size: 14}},
    paper_bgcolor: "#131313", plot_bgcolor: "#131313",
    font: {color: "#e5e5e5", family: "ui-monospace"},
    margin: {t: 40, b: 8, l: 8, r: 8},
    height: 260,
    showlegend: true,
    legend: {orientation: "h", y: -0.1},
  }, {displayModeBar: false});
}

// ──────────────────────────────────────────────────────────────────────────
// Plotly: surface bar
// ──────────────────────────────────────────────────────────────────────────
function renderSurfaceBar() {
  const entries = Object.entries(SUMMARY.by_surface).sort((a, b) => b[1] - a[1]);
  const labels = entries.map(e => e[0]);
  const values = entries.map(e => e[1]);
  Plotly.newPlot("surface-bar", [{
    type: "bar", orientation: "h",
    x: values, y: labels,
    marker: {color: "#3b82f6"},
    hovertemplate: "%{y}: %{x} rows<extra></extra>",
  }], {
    title: {text: "Surface types", font: {color: "#fbbf24", size: 14}},
    paper_bgcolor: "#131313", plot_bgcolor: "#131313",
    font: {color: "#e5e5e5", family: "ui-monospace", size: 11},
    margin: {t: 40, b: 32, l: 110, r: 16},
    height: 260,
    xaxis: {gridcolor: "#222", color: "#888"},
    yaxis: {automargin: true, color: "#e5e5e5"},
  }, {displayModeBar: false});
}

// ──────────────────────────────────────────────────────────────────────────
// Plotly: registries × states (stacked horizontal bar)
// ──────────────────────────────────────────────────────────────────────────
function renderRegistryBar() {
  const regNames = Object.entries(SUMMARY.by_registry)
    .map(([k, v]) => [k, (v.ACTIVE||0) + (v.DEFERRED||0) + (v.BLOCKED||0)])
    .sort((a, b) => b[1] - a[1])
    .map(e => e[0]);
  const active = regNames.map(r => SUMMARY.by_registry[r].ACTIVE || 0);
  const deferred = regNames.map(r => SUMMARY.by_registry[r].DEFERRED || 0);
  const blocked = regNames.map(r => SUMMARY.by_registry[r].BLOCKED || 0);

  Plotly.newPlot("registry-bar", [
    {type: "bar", orientation: "h", name: "ACTIVE", x: active, y: regNames, marker: {color: "#1e7a3e"}, hovertemplate: "%{y} ACTIVE: %{x}<extra></extra>"},
    {type: "bar", orientation: "h", name: "DEFERRED", x: deferred, y: regNames, marker: {color: "#7a5d1e"}, hovertemplate: "%{y} DEFERRED: %{x}<extra></extra>"},
    {type: "bar", orientation: "h", name: "BLOCKED", x: blocked, y: regNames, marker: {color: "#7a1e1e"}, hovertemplate: "%{y} BLOCKED: %{x}<extra></extra>"},
  ], {
    title: {text: "Rows per registry, by state", font: {color: "#fbbf24", size: 14}},
    barmode: "stack",
    paper_bgcolor: "#131313", plot_bgcolor: "#131313",
    font: {color: "#e5e5e5", family: "ui-monospace", size: 11},
    margin: {t: 40, b: 32, l: 240, r: 16},
    height: Math.max(420, regNames.length * 22),
    xaxis: {gridcolor: "#222", color: "#888"},
    yaxis: {automargin: true, color: "#e5e5e5"},
    legend: {orientation: "h", y: -0.05},
  }, {displayModeBar: false});
}

// ──────────────────────────────────────────────────────────────────────────
// Advisory-stale panel
// ──────────────────────────────────────────────────────────────────────────
function renderAdvisoryStale() {
  const items = SUMMARY.advisory_stale_rows;
  if (!items.length) {
    document.getElementById("advisory-stale-panel").innerHTML =
      '<div style="color:#6ee7b7">No advisory-stale rows. Every ACTIVE in-repo path resolves on disk.</div>';
    return;
  }
  // Group by registry
  const groups = {};
  for (const item of items) {
    if (!groups[item.registry]) groups[item.registry] = [];
    groups[item.registry].push(item);
  }
  const html = Object.entries(groups).map(([reg, rows]) => {
    const inner = rows.map(r => {
      const paths = r.advisory_stale_paths.map(([f, p]) => `<code>${p}</code> <span style="color:#666">(${f})</span>`).join("<br>");
      return `<tr><td><code>${r.id}</code></td><td><span class="badge ACTIVE">${r.surface}</span></td><td class="stale-list">${paths}</td></tr>`;
    }).join("");
    return `<details open style="margin-bottom:12px"><summary style="cursor:pointer; padding:6px 0; font-weight:600; color:#fbbf24">${reg} — ${rows.length} rows</summary><table>${inner}</table></details>`;
  }).join("");
  document.getElementById("advisory-stale-panel").innerHTML = html;
}

// ──────────────────────────────────────────────────────────────────────────
// All-rows table with filters + sort
// ──────────────────────────────────────────────────────────────────────────
let sortCol = "registry";
let sortDesc = false;

function populateFilterOptions() {
  const regSel = document.getElementById("filter-registry");
  const regs = [...new Set(ROWS.map(r => r.registry))].sort();
  for (const r of regs) {
    const opt = document.createElement("option");
    opt.value = r; opt.textContent = r;
    regSel.appendChild(opt);
  }
  const surfSel = document.getElementById("filter-surface");
  const surfs = [...new Set(ROWS.map(r => r.surface))].sort();
  for (const s of surfs) {
    const opt = document.createElement("option");
    opt.value = s; opt.textContent = s;
    surfSel.appendChild(opt);
  }
}

function renderTable() {
  const q = document.getElementById("filter-q").value.toLowerCase();
  const stF = document.getElementById("filter-state").value;
  const regF = document.getElementById("filter-registry").value;
  const surfF = document.getElementById("filter-surface").value;

  let filtered = ROWS.filter(r => {
    if (stF && r.state !== stF) return false;
    if (regF && r.registry !== regF) return false;
    if (surfF && r.surface !== surfF) return false;
    if (q) {
      const hay = `${r.id} ${r.name} ${r.description}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  filtered.sort((a, b) => {
    const av = String(a[sortCol] || "");
    const bv = String(b[sortCol] || "");
    const cmp = av.localeCompare(bv);
    return sortDesc ? -cmp : cmp;
  });

  document.getElementById("row-count").textContent =
    `${filtered.length} / ${ROWS.length} rows`;

  const tbody = document.getElementById("rows-tbody");
  tbody.innerHTML = filtered.map(r => {
    const badges = [
      `<span class="badge ${r.state}">${r.state}</span>`,
    ];
    if (r.n_advisory_stale > 0) badges.push(`<span class="badge stale" title="${r.n_advisory_stale} unverifiable paths">stale ${r.n_advisory_stale}</span>`);
    if (r.n_install_evidence > 0) badges.push(`<span class="badge install" title="${r.n_install_evidence} install-evidence paths">install ${r.n_install_evidence}</span>`);
    return `<tr>
      <td>${r.registry}</td>
      <td>${badges.join(" ")}</td>
      <td>${r.surface}</td>
      <td><code>${r.id}</code></td>
      <td>${r.name}</td>
      <td style="color:#aaa">${(r.description || "").substring(0, 140)}</td>
    </tr>`;
  }).join("");
}

document.getElementById("filter-q").addEventListener("input", renderTable);
document.getElementById("filter-state").addEventListener("change", renderTable);
document.getElementById("filter-registry").addEventListener("change", renderTable);
document.getElementById("filter-surface").addEventListener("change", renderTable);
document.querySelectorAll("#rows-table th").forEach(th => {
  th.addEventListener("click", () => {
    const col = th.dataset.col;
    if (sortCol === col) sortDesc = !sortDesc;
    else { sortCol = col; sortDesc = false; }
    renderTable();
  });
});

renderStats();
renderStatePie();
renderSurfaceBar();
renderRegistryBar();
renderAdvisoryStale();
populateFilterOptions();
renderTable();
</script>

</body>
</html>
"""


def main() -> int:
    """Entry point — parse registries, render report, write HTML."""
    rows = parse_registries(REPO_ROOT)
    s = summary(rows)
    payload = {
        "rows": slim_rows(rows),
        "summary": s,
    }
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = (HTML_TEMPLATE
            .replace("__GENERATED_AT__", generated_at)
            .replace("__EMBED_DATA__", json.dumps(payload, default=str)))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  size: {len(html):,} chars")
    print(f"  rows: {len(rows)}")
    print(f"  registries: {len(s['by_registry'])}")
    print(f"  advisory-stale: {len(s['advisory_stale_rows'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
