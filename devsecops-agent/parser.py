"""Parser utilities for Gitleaks, Trivy, and Semgrep JSON outputs."""

from __future__ import annotations

from typing import Any


def normalize_severity(raw: str | None) -> str:
    """Maps tool-specific severity values to LOW, MEDIUM, or HIGH."""
    if not raw:
        return "MEDIUM"

    value = raw.strip().lower()
    if value in {"critical", "high", "error"}:
        return "HIGH"
    if value in {"medium", "moderate", "warning"}:
        return "MEDIUM"
    return "LOW"


def parse_scan_results(scan_json: dict[str, Any]) -> list[dict[str, Any]]:
    """Parses mixed scan payloads and returns normalized issue dictionaries."""
    issues: list[dict[str, Any]] = []

    issues.extend(_parse_gitleaks(scan_json))
    issues.extend(_parse_trivy(scan_json))
    issues.extend(_parse_semgrep(scan_json))

    return issues


def _parse_gitleaks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Parses Gitleaks findings from a JSON payload."""
    findings = payload.get("Leaks") or payload.get("leaks") or []
    out: list[dict[str, Any]] = []

    for item in findings:
        if not isinstance(item, dict):
            continue

        out.append(
            {
                "file": str(item.get("File") or item.get("file") or item.get("Path") or "unknown"),
                "issue": str(item.get("RuleID") or item.get("rule_id") or "gitleaks-finding"),
                "severity": normalize_severity(str(item.get("Severity") or "HIGH")),
                "message": str(item.get("Description") or item.get("description") or "Potential secret detected"),
                "tool": "Gitleaks",
            }
        )

    return out


def _parse_trivy(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Parses Trivy vulnerability findings from a JSON payload."""
    out: list[dict[str, Any]] = []
    results = payload.get("Results") or payload.get("results") or []

    for result in results:
        if not isinstance(result, dict):
            continue

        target = str(result.get("Target") or result.get("target") or "unknown")
        vulns = result.get("Vulnerabilities") or result.get("vulnerabilities") or []

        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue

            pkg = str(vuln.get("PkgName") or vuln.get("pkgName") or "package")
            vuln_id = str(vuln.get("VulnerabilityID") or vuln.get("vulnerabilityId") or "trivy-vuln")
            title = str(vuln.get("Title") or vuln.get("title") or vuln.get("Description") or "Trivy vulnerability")
            severity = normalize_severity(str(vuln.get("Severity") or "MEDIUM"))

            out.append(
                {
                    "file": target,
                    "issue": f"{pkg}:{vuln_id}",
                    "severity": severity,
                    "message": title,
                    "tool": "Trivy",
                }
            )

    return out


def _parse_semgrep(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Parses Semgrep findings from a JSON payload."""
    out: list[dict[str, Any]] = []
    results = payload.get("results") or payload.get("Results") or []

    for result in results:
        if not isinstance(result, dict):
            continue

        # Skip Trivy entries when both tools share the "results" key.
        if "Vulnerabilities" in result or "vulnerabilities" in result:
            continue

        extra = result.get("extra") if isinstance(result.get("extra"), dict) else {}
        out.append(
            {
                "file": str(result.get("path") or result.get("file") or "unknown"),
                "issue": str(result.get("check_id") or result.get("checkId") or result.get("rule_id") or "semgrep-finding"),
                "severity": normalize_severity(str(extra.get("severity") or result.get("severity") or "MEDIUM")),
                "message": str(extra.get("message") or result.get("message") or "Potential insecure pattern"),
                "tool": "Semgrep",
            }
        )

    return out
