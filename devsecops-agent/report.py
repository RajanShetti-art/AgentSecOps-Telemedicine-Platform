"""Generate a PPT-style HTML security report from the consolidated security dashboard.

All text and table cells are rendered as plain HTML so every piece of content
is selectable and copyable with a standard browser selection or Ctrl+A / Ctrl+C.

Usage:
    python report.py --input security-dashboard.json --output security-report.html
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _esc(value: Any) -> str:
    """HTML-escape a value for safe embedding in text nodes."""
    return html.escape(str(value) if value is not None else "")


def _severity_class(sev: str) -> str:
    s = str(sev).upper()
    if s in ("CRITICAL", "HIGH", "ERROR"):
        return "sev-high"
    if s in ("MEDIUM", "WARNING"):
        return "sev-medium"
    return "sev-low"


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def _slide(title: str, body: str, slide_number: int) -> str:
    return f"""
<section class="slide" id="slide-{slide_number}">
  <div class="slide-header">
    <span class="slide-num">{slide_number}</span>
    <h2>{_esc(title)}</h2>
  </div>
  <div class="slide-body">
    {body}
  </div>
</section>
"""


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    th = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body_rows = ""
    for row in rows:
        tds = "".join(f"<td>{_esc(cell)}</td>" for cell in row)
        body_rows += f"<tr>{tds}</tr>\n"
    if not body_rows:
        colspan = len(headers)
        body_rows = f'<tr><td colspan="{colspan}" class="empty">No findings</td></tr>'
    return f"""
<div class="table-wrap">
<table>
  <thead><tr>{th}</tr></thead>
  <tbody>{body_rows}</tbody>
</table>
</div>
"""


def _kv_table(pairs: list[tuple[str, Any]]) -> str:
    rows = "".join(f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in pairs)
    return f"""
<div class="table-wrap">
<table class="kv-table">
  <tbody>{rows}</tbody>
</table>
</div>
"""


def _pill(text: str, cls: str) -> str:
    return f'<span class="pill {cls}">{_esc(text)}</span>'


# ---------------------------------------------------------------------------
# Slide: title / summary
# ---------------------------------------------------------------------------

def build_title_slide(dashboard: dict[str, Any]) -> str:
    tools_checked = []
    for key, label in [
        ("semgrep", "Semgrep SAST"),
        ("trivy_fs", "Trivy (filesystem)"),
        ("kubescape", "Kubescape"),
        ("checkov", "Checkov"),
        ("kube_bench", "kube-bench"),
        ("kyverno", "Kyverno"),
        ("frontend_npm_audit", "npm audit"),
    ]:
        status = "✓" if dashboard.get(key) else "—"
        tools_checked.append((label, status))

    kv = _kv_table(tools_checked)
    body = f"""
<p class="lead">Automated security scan results across all pipeline tools.
All content on each slide can be selected and copied with your keyboard or mouse.</p>
{kv}
"""
    return _slide("AgentSecOps — Security Report", body, 1)


# ---------------------------------------------------------------------------
# Slide: Semgrep SAST
# ---------------------------------------------------------------------------

def build_semgrep_slide(dashboard: dict[str, Any]) -> str:
    data = dashboard.get("semgrep", {})
    results = data.get("results", [])
    rows = []
    for r in results:
        extra = r.get("extra", {})
        sev = extra.get("severity", "UNKNOWN")
        path = r.get("path", "")
        line = r.get("start", {}).get("line", "")
        rule = r.get("check_id", "")
        msg = extra.get("message", "")
        rows.append([
            _pill(sev, _severity_class(sev)),
            path,
            line,
            rule,
            msg,
        ])

    # Render pill HTML directly (already escaped inside _pill)
    th = "".join(f"<th>{_esc(h)}</th>" for h in ["Severity", "File", "Line", "Rule", "Message"])
    body_rows = ""
    for row in rows:
        # first cell is already HTML
        tds = f"<td>{row[0]}</td>" + "".join(f"<td>{_esc(cell)}</td>" for cell in row[1:])
        body_rows += f"<tr>{tds}</tr>\n"
    if not body_rows:
        body_rows = '<tr><td colspan="5" class="empty">No findings</td></tr>'

    table = f"""
<div class="table-wrap">
<table>
  <thead><tr>{th}</tr></thead>
  <tbody>{body_rows}</tbody>
</table>
</div>
"""
    total = len(rows)
    high = sum(1 for r in rows if "sev-high" in r[0])
    body = f'<p>Total findings: <strong>{total}</strong> &nbsp; High/Critical: <strong>{high}</strong></p>' + table
    return _slide("Semgrep — SAST Results", body, 2)


# ---------------------------------------------------------------------------
# Slide: Trivy filesystem
# ---------------------------------------------------------------------------

def _trivy_rows(data: dict[str, Any]) -> list[list[Any]]:
    rows = []
    for result in data.get("Results", []):
        target = result.get("Target", "")
        for vuln in result.get("Vulnerabilities") or []:
            rows.append([
                vuln.get("Severity", ""),
                target,
                vuln.get("PkgName", ""),
                vuln.get("VulnerabilityID", ""),
                vuln.get("InstalledVersion", ""),
                vuln.get("FixedVersion", ""),
                vuln.get("Title", ""),
            ])
    return rows


def build_trivy_fs_slide(dashboard: dict[str, Any]) -> str:
    rows = _trivy_rows(dashboard.get("trivy_fs", {}))
    sev_rows: list[list[Any]] = []
    for row in rows:
        sev = str(row[0]).upper()
        sev_rows.append([_pill(sev, _severity_class(sev))] + row[1:])

    headers = ["Severity", "Target", "Package", "CVE", "Installed", "Fixed", "Title"]
    th = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body_rows = ""
    for row in sev_rows:
        tds = f"<td>{row[0]}</td>" + "".join(f"<td>{_esc(cell)}</td>" for cell in row[1:])
        body_rows += f"<tr>{tds}</tr>\n"
    if not body_rows:
        body_rows = f'<tr><td colspan="{len(headers)}" class="empty">No findings</td></tr>'
    table = f"""
<div class="table-wrap">
<table>
  <thead><tr>{th}</tr></thead>
  <tbody>{body_rows}</tbody>
</table>
</div>
"""
    total = len(rows)
    high = sum(1 for r in rows if str(r[0]).upper() in ("HIGH", "CRITICAL"))
    body = f'<p>Total vulnerabilities: <strong>{total}</strong> &nbsp; High/Critical: <strong>{high}</strong></p>' + table
    return _slide("Trivy — Filesystem Vulnerabilities", body, 3)


# ---------------------------------------------------------------------------
# Slide: Trivy image scans
# ---------------------------------------------------------------------------

def build_trivy_images_slide(dashboard: dict[str, Any]) -> str:
    images = dashboard.get("trivy_images", {})
    all_rows: list[list[Any]] = []
    for service, data in images.items():
        for row in _trivy_rows(data):
            all_rows.append([service] + row)

    sev_rows = []
    for row in all_rows:
        sev = str(row[1]).upper()
        sev_rows.append([row[0], _pill(sev, _severity_class(sev))] + row[2:])

    headers = ["Service", "Severity", "Target", "Package", "CVE", "Installed", "Fixed", "Title"]
    th = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    body_rows = ""
    for row in sev_rows:
        tds = f"<td>{_esc(row[0])}</td><td>{row[1]}</td>" + "".join(f"<td>{_esc(cell)}</td>" for cell in row[2:])
        body_rows += f"<tr>{tds}</tr>\n"
    if not body_rows:
        body_rows = f'<tr><td colspan="{len(headers)}" class="empty">No findings</td></tr>'
    table = f"""
<div class="table-wrap">
<table>
  <thead><tr>{th}</tr></thead>
  <tbody>{body_rows}</tbody>
</table>
</div>
"""
    total = len(all_rows)
    high = sum(1 for r in all_rows if str(r[1]).upper() in ("HIGH", "CRITICAL"))
    body = f'<p>Total: <strong>{total}</strong> &nbsp; High/Critical: <strong>{high}</strong></p>' + table
    return _slide("Trivy — Container Image Vulnerabilities", body, 4)


# ---------------------------------------------------------------------------
# Slide: Checkov IaC
# ---------------------------------------------------------------------------

def build_checkov_slide(dashboard: dict[str, Any]) -> str:
    data = dashboard.get("checkov", {})
    checks = data.get("results", {})
    failed = checks.get("failed_checks", [])
    rows = []
    for c in failed:
        rows.append([
            c.get("check_id", ""),
            c.get("check_type", ""),
            c.get("resource", ""),
            c.get("file_path", ""),
            c.get("check_result", {}).get("result", ""),
        ])
    table = _table(["Check ID", "Type", "Resource", "File", "Result"], rows)
    body = f'<p>Failed checks: <strong>{len(rows)}</strong></p>' + table
    return _slide("Checkov — IaC Security Findings", body, 5)


# ---------------------------------------------------------------------------
# Slide: Kubescape
# ---------------------------------------------------------------------------

def build_kubescape_slide(dashboard: dict[str, Any]) -> str:
    data = dashboard.get("kubescape", {})
    results = data.get("results", []) if isinstance(data.get("results"), list) else []
    rows = []
    for r in results:
        controls = r.get("controls", []) if isinstance(r.get("controls"), list) else []
        for ctrl in controls:
            status = ctrl.get("status", {})
            if isinstance(status, dict):
                result_val = status.get("status", "")
            else:
                result_val = str(status)
            rows.append([
                ctrl.get("controlID", ""),
                ctrl.get("name", ""),
                result_val,
                r.get("name", ""),
            ])
    table = _table(["Control ID", "Control Name", "Status", "Resource"], rows)
    body = f'<p>Controls evaluated: <strong>{len(rows)}</strong></p>' + table
    return _slide("Kubescape — Kubernetes Security Posture", body, 6)


# ---------------------------------------------------------------------------
# Slide: npm audit
# ---------------------------------------------------------------------------

def build_npm_slide(dashboard: dict[str, Any]) -> str:
    data = dashboard.get("frontend_npm_audit", {})
    vulns = data.get("vulnerabilities", {})
    rows = []
    for pkg, info in vulns.items():
        sev = info.get("severity", "")
        via_raw = info.get("via", [""])
        via = via_raw[0] if isinstance(via_raw, list) else str(via_raw)
        rows.append([
            _pill(sev.upper(), _severity_class(sev)),
            pkg,
            via,
            info.get("fixAvailable", False),
        ])
    th = "".join(f"<th>{_esc(h)}</th>" for h in ["Severity", "Package", "Via", "Fix Available"])
    body_rows = ""
    for row in rows:
        tds = f"<td>{row[0]}</td>" + "".join(f"<td>{_esc(cell)}</td>" for cell in row[1:])
        body_rows += f"<tr>{tds}</tr>\n"
    if not body_rows:
        body_rows = '<tr><td colspan="4" class="empty">No vulnerabilities</td></tr>'
    table = f"""
<div class="table-wrap">
<table>
  <thead><tr>{th}</tr></thead>
  <tbody>{body_rows}</tbody>
</table>
</div>
"""
    meta = data.get("metadata", {})
    total_vuln = meta.get("vulnerabilities", {})
    total = sum(total_vuln.values()) if isinstance(total_vuln, dict) else len(rows)
    body = f'<p>Total vulnerable packages: <strong>{total}</strong></p>' + table
    return _slide("npm audit — Frontend SCA", body, 7)


# ---------------------------------------------------------------------------
# Slide: kube-bench
# ---------------------------------------------------------------------------

def build_kube_bench_slide(dashboard: dict[str, Any]) -> str:
    data = dashboard.get("kube_bench", {})
    if data.get("skipped"):
        body = "<p>kube-bench was not executed in this pipeline run (requires cluster/node access).</p>"
        return _slide("kube-bench — CIS Benchmark", body, 8)
    rows = []
    for group in data.get("Controls", []) or []:
        for test in group.get("tests", []) or []:
            for result in test.get("results", []) or []:
                rows.append([
                    result.get("test_number", ""),
                    result.get("status", ""),
                    result.get("test_desc", ""),
                    result.get("remediation", ""),
                ])
    table = _table(["Test Number", "Status", "Description", "Remediation"], rows)
    body = f'<p>CIS checks: <strong>{len(rows)}</strong></p>' + table
    return _slide("kube-bench — CIS Benchmark", body, 8)


# ---------------------------------------------------------------------------
# Slide: Kyverno
# ---------------------------------------------------------------------------

def build_kyverno_slide(dashboard: dict[str, Any]) -> str:
    data = dashboard.get("kyverno", {})
    if data.get("skipped"):
        body = "<p>Kyverno policy tests were skipped (no policies found).</p>"
        return _slide("Kyverno — Policy Report", body, 9)
    results = data.get("results", []) if isinstance(data.get("results"), list) else []
    rows = []
    for r in results:
        rows.append([
            r.get("policy", ""),
            r.get("rule", ""),
            r.get("resource", {}).get("name", "") if isinstance(r.get("resource"), dict) else "",
            r.get("result", ""),
            r.get("message", ""),
        ])
    table = _table(["Policy", "Rule", "Resource", "Result", "Message"], rows)
    body = f'<p>Policy results: <strong>{len(rows)}</strong></p>' + table
    return _slide("Kyverno — Policy Report", body, 9)


# ---------------------------------------------------------------------------
# HTML skeleton
# ---------------------------------------------------------------------------

_CSS = """
:root {
  --bg: #1a1d2e;
  --slide-bg: #ffffff;
  --header-bg: #0f4c81;
  --header-text: #ffffff;
  --accent: #2563eb;
  --muted: #6b7280;
  --line: #e5e7eb;
  --high: #b91c1c;
  --medium: #d97706;
  --low: #166534;
  --high-bg: #fee2e2;
  --medium-bg: #fef3c7;
  --low-bg: #dcfce7;
  --font: "Segoe UI", Arial, sans-serif;
}

*, *::before, *::after {
  box-sizing: border-box;
  /* Ensure every element is selectable so users can copy anything */
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
}

body {
  margin: 0;
  padding: 32px 16px;
  background: var(--bg);
  font-family: var(--font);
  color: #1f2937;
}

h1.report-title {
  text-align: center;
  color: #ffffff;
  font-size: 1.6rem;
  margin-bottom: 32px;
  letter-spacing: .03em;
}

.slide {
  background: var(--slide-bg);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,.35);
  margin: 0 auto 40px;
  max-width: 1100px;
  overflow: hidden;
  page-break-inside: avoid;
}

.slide-header {
  background: var(--header-bg);
  color: var(--header-text);
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 22px;
}

.slide-num {
  background: rgba(255,255,255,.2);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: .85rem;
  flex-shrink: 0;
}

.slide-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
}

.slide-body {
  padding: 20px 22px;
}

p.lead {
  color: var(--muted);
  margin: 0 0 14px;
  line-height: 1.6;
}

/* Tables */
.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: .83rem;
  margin-top: 8px;
}

th {
  background: #f1f5f9;
  border: 1px solid var(--line);
  padding: 8px 10px;
  text-align: left;
  white-space: nowrap;
}

td {
  border: 1px solid var(--line);
  padding: 7px 10px;
  vertical-align: top;
  /* Long values should wrap instead of overflowing */
  word-break: break-word;
}

tr:nth-child(even) td {
  background: #f9fafb;
}

table.kv-table th {
  width: 220px;
  background: #f1f5f9;
}

td.empty {
  color: var(--muted);
  font-style: italic;
}

/* Severity pills */
.pill {
  display: inline-block;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: .75rem;
  font-weight: 600;
  white-space: nowrap;
}

.sev-high  { background: var(--high-bg);   color: var(--high);   }
.sev-medium{ background: var(--medium-bg); color: var(--medium); }
.sev-low   { background: var(--low-bg);    color: var(--low);    }

@media print {
  body { background: #fff; padding: 0; }
  h1.report-title { color: #000; }
  .slide { box-shadow: none; border: 1px solid #ccc; margin-bottom: 24px; }
}
"""

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentSecOps Security Report</title>
<style>
{css}
</style>
</head>
<body>
<h1 class="report-title">AgentSecOps — Security Pipeline Report</h1>
{slides}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def generate_report(input_path: str, output_path: str) -> None:
    dashboard = _load(input_path)

    slides = "".join([
        build_title_slide(dashboard),
        build_semgrep_slide(dashboard),
        build_trivy_fs_slide(dashboard),
        build_trivy_images_slide(dashboard),
        build_checkov_slide(dashboard),
        build_kubescape_slide(dashboard),
        build_npm_slide(dashboard),
        build_kube_bench_slide(dashboard),
        build_kyverno_slide(dashboard),
    ])

    html_content = _HTML_TEMPLATE.format(css=_CSS, slides=slides)
    Path(output_path).write_text(html_content, encoding="utf-8")
    print(f"Report written to {output_path}")


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate PPT-style HTML security report")
    p.add_argument("--input", default="security-dashboard.json", help="Path to consolidated security-dashboard.json")
    p.add_argument("--output", default="security-report.html", help="Output HTML file path")
    return p


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    generate_report(args.input, args.output)
