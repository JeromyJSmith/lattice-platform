#!/usr/bin/env python3
"""Aggregate all benchy reports/*.json into a single interactive HTML report.

Outputs `LATTICE_BENCH_REPORT.html` with:
- Summary cards (totals, leader, slowest)
- Per-benchmark grouped bar charts (correctness, tok/s, avg duration)
- Cross-benchmark model leaderboard
- Per-test drilldown table (sortable, filterable)
- All raw data inlined for offline viewing

Uses Plotly.js from CDN. Single HTML file, drag into a browser, no server required.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from html import escape
from pathlib import Path

REPORTS_DIR = Path(__file__).parent / "reports"
OUTPUT = Path(__file__).parent.parent / "LATTICE_BENCH_REPORT.html"

# Pattern to recognise LATTICE benchmark reports (skip earlier sample reports)
LATTICE_PREFIX = ("LATTICE_", "Bench_", "Benchy_", "benchy_")


def short_name(model: str) -> str:
    """`mlx~prism-ml/Ternary-Bonsai-8B-mlx-2bit` -> `Bonsai-8B`."""
    name = model.split("~", 1)[-1].split("/", 1)[-1]
    name = re.sub(r"-mlx-(\d+)bit$", "", name)
    name = re.sub(r"-MLX-(\d+)bit$", "", name)
    name = re.sub(r"-UD-(\d+)bit$", "", name)
    name = name.replace("Ternary-", "")
    name = re.sub(r"-Instruct-(\d+)bit$", "", name)
    name = re.sub(r"-(\d+)bit$", "", name)
    return name


def load_reports() -> list[dict]:
    reports = []
    for f in sorted(REPORTS_DIR.glob("*.json")):
        if not f.name.upper().startswith(("LATTICE_", "BENCH_")):
            continue
        try:
            with f.open() as fp:
                data = json.load(fp)
            data["_filename"] = f.name
            data["_mtime"] = datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
            reports.append(data)
        except Exception as e:
            print(f"skip {f.name}: {e}", file=sys.stderr)
    return reports


def cross_bench_stats(reports: list[dict]) -> dict:
    """Aggregate per-model across all benchmarks."""
    agg: dict[str, dict] = {}
    for r in reports:
        for m in r.get("models", []):
            key = m["model"]
            row = agg.setdefault(key, {
                "model": key,
                "short": short_name(key),
                "correct_total": 0,
                "incorrect_total": 0,
                "total_runs": 0,
                "tps_sum": 0.0,
                "ms_sum": 0.0,
                "tps_count": 0,
                "load_sum": 0.0,
                "load_count": 0,
                "benchmarks": [],
            })
            c = m.get("correct_count") or 0
            ic = m.get("incorrect_count") or 0
            row["correct_total"] += c
            row["incorrect_total"] += ic
            n = c + ic
            row["total_runs"] += n
            tps = m.get("average_tokens_per_second") or 0.0
            ms = m.get("average_total_duration_ms") or 0.0
            load = m.get("average_load_duration_ms") or 0.0
            if tps > 0:
                row["tps_sum"] += tps * n
                row["tps_count"] += n
            if ms > 0:
                row["ms_sum"] += ms * n
            if load > 0:
                row["load_sum"] += load * n
                row["load_count"] += n
            row["benchmarks"].append(r.get("benchmark_name", r["_filename"]))
    for row in agg.values():
        row["accuracy"] = (row["correct_total"] / row["total_runs"]) if row["total_runs"] else 0.0
        row["avg_tps"] = (row["tps_sum"] / row["tps_count"]) if row["tps_count"] else 0.0
        row["avg_ms"] = (row["ms_sum"] / row["total_runs"]) if row["total_runs"] else 0.0
        row["avg_load_ms"] = (row["load_sum"] / row["load_count"]) if row["load_count"] else 0.0
    return agg


def build_html(reports: list[dict]) -> str:
    cross = cross_bench_stats(reports)
    # Leaderboard
    leaderboard = sorted(cross.values(), key=lambda x: (-x["accuracy"], -x["avg_tps"]))

    bench_summaries = []
    for r in reports:
        models_data = []
        for m in r.get("models", []):
            n = (m.get("correct_count") or 0) + (m.get("incorrect_count") or 0)
            models_data.append({
                "model": short_name(m["model"]),
                "full": m["model"],
                "correct": m.get("correct_count") or 0,
                "incorrect": m.get("incorrect_count") or 0,
                "total": n,
                "accuracy": ((m.get("correct_count") or 0) / n) if n else 0.0,
                "tps": m.get("average_tokens_per_second") or 0.0,
                "total_ms": m.get("average_total_duration_ms") or 0.0,
                "load_ms": m.get("average_load_duration_ms") or 0.0,
            })
        bench_summaries.append({
            "name": r.get("benchmark_name", r["_filename"]),
            "purpose": r.get("purpose", ""),
            "file": r["_filename"],
            "mtime": r["_mtime"],
            "overall_accuracy": r.get("overall_accuracy") or 0,
            "overall_correct": r.get("overall_correct_count") or 0,
            "models": models_data,
            "n_prompts": len(r.get("prompt_iterations") or []),
        })

    drilldown = []
    for r in reports:
        for m in r.get("models", []):
            for res in m.get("results", []):
                resp = (res.get("prompt_response") or {})
                drilldown.append({
                    "bench": r.get("benchmark_name", r["_filename"]),
                    "model": short_name(m["model"]),
                    "prompt_idx": res.get("index"),
                    "expected": res.get("expected_result", ""),
                    "execution": (res.get("execution_result") or "")[:300],
                    "correct": res.get("correct", False),
                    "tps": resp.get("tokens_per_second", 0),
                    "duration_ms": resp.get("total_duration_ms", 0),
                    "response_preview": (resp.get("response", "") or "")[:200],
                })

    total_runs = sum(r["total"] for b in bench_summaries for r in b["models"])
    total_correct = sum(r["correct"] for b in bench_summaries for r in b["models"])

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "machine": "Apple M3 Max, 64GB unified memory",
        "totals": {
            "benchmarks": len(bench_summaries),
            "runs": total_runs,
            "correct": total_correct,
            "accuracy": (total_correct / total_runs) if total_runs else 0,
            "unique_models": len(cross),
        },
        "leaderboard": leaderboard,
        "benchmarks": bench_summaries,
        "drilldown": drilldown,
    }
    payload_json = json.dumps(payload, default=str)

    css = """
    :root { --bg:#0a0e14; --fg:#e6edf3; --muted:#7d8590; --card:#161b22; --border:#30363d;
            --accent:#7ee787; --warn:#d29922; --bad:#f85149; --bonsai:#a5d6ff; }
    * { box-sizing: border-box; }
    html, body { background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif; margin: 0; padding: 0; line-height: 1.5; }
    .wrap { max-width: 1500px; margin: 0 auto; padding: 24px; }
    h1 { font-size: 32px; margin: 0 0 4px; letter-spacing: -0.02em; }
    h2 { font-size: 22px; margin: 32px 0 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    h3 { font-size: 16px; margin: 16px 0 8px; color: var(--muted); font-weight: 500; }
    .subtitle { color: var(--muted); margin: 0 0 24px; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0 24px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
    .card .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
    .card .value { font-size: 26px; font-weight: 600; margin-top: 4px; }
    .card.accent .value { color: var(--accent); }
    .card.warn .value { color: var(--warn); }
    .bench { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin: 16px 0; }
    .bench-head { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 12px; }
    .bench-head h3 { color: var(--fg); margin: 0; font-size: 18px; }
    .bench-head .meta { color: var(--muted); font-size: 13px; }
    .bench-purpose { color: var(--muted); font-size: 14px; margin: 4px 0 16px; font-style: italic; }
    .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }
    .chart { background: #0d1117; border: 1px solid var(--border); border-radius: 6px; padding: 8px; min-height: 320px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 12px; }
    th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); }
    th { background: #0d1117; color: var(--muted); font-weight: 500; cursor: pointer; user-select: none; }
    th:hover { color: var(--fg); }
    tr:hover td { background: #0d1117; }
    td.num { text-align: right; font-variant-numeric: tabular-nums; }
    .ok { color: var(--accent); }
    .bad { color: var(--bad); }
    .pill { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; background: #0d1117; border: 1px solid var(--border); color: var(--muted); }
    .filter-bar { display: flex; gap: 8px; margin: 12px 0; align-items: center; flex-wrap: wrap; }
    .filter-bar input, .filter-bar select { background: #0d1117; color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 6px 10px; font-size: 13px; }
    .response-cell { font-family: 'SF Mono', Menlo, monospace; font-size: 11px; white-space: pre-wrap; word-break: break-word; max-width: 400px; color: var(--muted); }
    .footer { color: var(--muted); font-size: 12px; margin-top: 32px; text-align: center; padding-top: 16px; border-top: 1px solid var(--border); }
    """

    js = """
const D = window.LATTICE_REPORT;
const layoutBase = {
  paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
  font: { color: '#e6edf3', size: 12 }, margin: { t: 40, r: 12, b: 80, l: 56 },
  xaxis: { gridcolor: '#30363d', tickangle: -30 },
  yaxis: { gridcolor: '#30363d' },
  legend: { orientation: 'h', y: -0.4 },
};

function buildLeaderboard() {
  const top = [...D.leaderboard].sort((a,b) => b.accuracy - a.accuracy);
  const x = top.map(r => r.short);
  const trace1 = { x, y: top.map(r => Math.round(r.accuracy * 1000)/10), type: 'bar', name: 'Accuracy %', marker: { color: '#7ee787' } };
  const trace2 = { x, y: top.map(r => Math.round(r.avg_tps)), type: 'bar', name: 'Avg tok/s', yaxis: 'y2', marker: { color: '#a5d6ff' } };
  Plotly.newPlot('chart-leaderboard', [trace1, trace2], {
    ...layoutBase,
    title: 'Cross-benchmark leaderboard — accuracy vs throughput',
    yaxis: { ...layoutBase.yaxis, title: 'Accuracy (%)', range: [0, 100] },
    yaxis2: { title: 'tok/s', overlaying: 'y', side: 'right', gridcolor: 'transparent' },
    barmode: 'group',
  }, {displaylogo: false, responsive: true});
}

function buildBenchCharts() {
  D.benchmarks.forEach((b, i) => {
    const slug = 'b' + i;
    const x = b.models.map(m => m.model);
    const traces = [
      { x, y: b.models.map(m => Math.round(m.accuracy * 1000)/10), type: 'bar', name: 'Accuracy %', marker: { color: '#7ee787' } },
    ];
    Plotly.newPlot(`chart-acc-${slug}`, traces, {
      ...layoutBase,
      title: 'Accuracy (%)',
      yaxis: { ...layoutBase.yaxis, range: [0, 100] },
    }, {displaylogo: false, responsive: true});

    Plotly.newPlot(`chart-tps-${slug}`, [{
      x, y: b.models.map(m => m.tps), type: 'bar', name: 'tok/s', marker: { color: '#a5d6ff' },
    }], { ...layoutBase, title: 'Throughput (tokens/sec)' }, {displaylogo: false, responsive: true});

    Plotly.newPlot(`chart-ms-${slug}`, [
      { x, y: b.models.map(m => Math.round(m.load_ms)), type: 'bar', name: 'Load ms', marker: { color: '#d29922' } },
      { x, y: b.models.map(m => Math.round(m.total_ms - m.load_ms)), type: 'bar', name: 'Generate ms', marker: { color: '#a5d6ff' } },
    ], { ...layoutBase, title: 'Latency breakdown (ms per prompt)', barmode: 'stack' }, {displaylogo: false, responsive: true});
  });
}

function buildDrilldown() {
  const tbody = document.querySelector('#drilldown-table tbody');
  const filterBench = document.querySelector('#filter-bench');
  const filterModel = document.querySelector('#filter-model');
  const filterText = document.querySelector('#filter-text');
  const filterCorrect = document.querySelector('#filter-correct');

  const benchSet = new Set(D.drilldown.map(d => d.bench));
  const modelSet = new Set(D.drilldown.map(d => d.model));
  [...benchSet].sort().forEach(b => filterBench.add(new Option(b, b)));
  [...modelSet].sort().forEach(m => filterModel.add(new Option(m, m)));

  function render() {
    const fb = filterBench.value;
    const fm = filterModel.value;
    const ft = filterText.value.toLowerCase();
    const fc = filterCorrect.value;
    const rows = D.drilldown.filter(d => {
      if (fb && d.bench !== fb) return false;
      if (fm && d.model !== fm) return false;
      if (fc === 'ok' && !d.correct) return false;
      if (fc === 'bad' && d.correct) return false;
      if (ft) {
        const hay = (d.bench + ' ' + d.model + ' ' + d.expected + ' ' + d.response_preview + ' ' + d.execution).toLowerCase();
        if (!hay.includes(ft)) return false;
      }
      return true;
    });
    tbody.innerHTML = rows.map(d => `<tr>
      <td>${d.bench}</td>
      <td><span class="pill">${d.model}</span></td>
      <td class="num">${d.prompt_idx}</td>
      <td class="${d.correct ? 'ok' : 'bad'}">${d.correct ? '✓' : '✗'}</td>
      <td class="num">${Math.round(d.tps)}</td>
      <td class="num">${Math.round(d.duration_ms)}</td>
      <td><code>${escapeHTML(String(d.expected))}</code></td>
      <td class="response-cell">${escapeHTML(d.execution)}</td>
    </tr>`).join('');
    document.querySelector('#row-count').textContent = `${rows.length} rows`;
  }

  [filterBench, filterModel, filterCorrect].forEach(el => el.addEventListener('change', render));
  filterText.addEventListener('input', render);

  // Column sort
  document.querySelectorAll('#drilldown-table thead th').forEach((th, idx) => {
    th.addEventListener('click', () => {
      D.drilldown.sort((a, b) => {
        const av = Object.values(a)[idx];
        const bv = Object.values(b)[idx];
        return typeof av === 'number' ? bv - av : String(av).localeCompare(String(bv));
      });
      render();
    });
  });

  render();
}

function escapeHTML(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

window.addEventListener('DOMContentLoaded', () => {
  buildLeaderboard();
  buildBenchCharts();
  buildDrilldown();
});
"""

    # Build per-benchmark blocks
    bench_blocks = []
    for i, b in enumerate(bench_summaries):
        slug = f"b{i}"
        bench_blocks.append(f"""
<div class="bench">
  <div class="bench-head">
    <h3>{escape(b['name'])}</h3>
    <div class="meta">
      <span class="pill">{b['n_prompts']} prompts</span>
      <span class="pill">{len(b['models'])} models</span>
      <span class="pill">{b['mtime']}</span>
    </div>
  </div>
  <p class="bench-purpose">{escape(b['purpose'])}</p>
  <div class="chart-grid">
    <div class="chart" id="chart-acc-{slug}"></div>
    <div class="chart" id="chart-tps-{slug}"></div>
    <div class="chart" id="chart-ms-{slug}"></div>
  </div>
</div>
""")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>LATTICE — Local-Model Benchmark Report</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <h1>LATTICE Local-Model Benchmark Report</h1>
  <p class="subtitle">Generated {payload['generated_at']} on {payload['machine']}.
     All models run locally via MLX (zero API cost). Click column headers to sort drilldown.</p>

  <div class="cards">
    <div class="card"><div class="label">Benchmarks</div><div class="value">{payload['totals']['benchmarks']}</div></div>
    <div class="card"><div class="label">Total runs</div><div class="value">{payload['totals']['runs']}</div></div>
    <div class="card accent"><div class="label">Correct</div><div class="value">{payload['totals']['correct']} <small style="font-size:14px;color:var(--muted)">({payload['totals']['accuracy']*100:.0f}%)</small></div></div>
    <div class="card"><div class="label">Unique models</div><div class="value">{payload['totals']['unique_models']}</div></div>
    <div class="card warn"><div class="label">Total API cost</div><div class="value">$0.00</div></div>
  </div>

  <h2>Cross-benchmark leaderboard</h2>
  <div class="chart" id="chart-leaderboard" style="min-height: 480px;"></div>

  <h2>Per-benchmark details</h2>
  {''.join(bench_blocks)}

  <h2>Drilldown — every test run</h2>
  <div class="filter-bar">
    <select id="filter-bench"><option value="">All benchmarks</option></select>
    <select id="filter-model"><option value="">All models</option></select>
    <select id="filter-correct"><option value="">All results</option><option value="ok">Correct only</option><option value="bad">Failed only</option></select>
    <input id="filter-text" type="text" placeholder="Search expected/response/error...">
    <span id="row-count" style="color: var(--muted); font-size:13px;"></span>
  </div>
  <table id="drilldown-table">
    <thead><tr>
      <th>Benchmark</th>
      <th>Model</th>
      <th>#</th>
      <th>Result</th>
      <th>tok/s</th>
      <th>ms</th>
      <th>Expected</th>
      <th>Execution / error</th>
    </tr></thead>
    <tbody></tbody>
  </table>

  <div class="footer">
    LATTICE Meta-Harness · {len(reports)} report files · Plotly.js {{ chart engine }} · drag this file anywhere — it's self-contained
  </div>
</div>

<script>
window.LATTICE_REPORT = {payload_json};
</script>
<script>{js}</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Aggregate Benchy reports into one interactive HTML.")
    parser.add_argument("--out", default=str(OUTPUT))
    args = parser.parse_args()

    reports = load_reports()
    if not reports:
        print(f"No LATTICE_* reports in {REPORTS_DIR}", file=sys.stderr)
        return 1
    html = build_html(reports)
    out = Path(args.out)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size:,} bytes, {len(reports)} reports)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
