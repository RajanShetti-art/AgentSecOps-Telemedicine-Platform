"""Utilities for normalizing scan output from security tools."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from devsecops_agent.models import Finding

_SEVERITY_MAP = {
    "critical": "HIGH",
    "high": "HIGH",
    "medium": "MEDIUM",
    "moderate": "MEDIUM",
    "low": "LOW",
    "info": "LOW",
    "unknown": "MEDIUM",
}


def _normalize_severity(raw_severity: str | None) -> str:
    """Maps scanner severities to LOW, MEDIUM, or HIGH."""
    if not raw_severity:
        return "MEDIUM"
    return _SEVERITY_MAP.get(raw_severity.strip().lower(), "MEDIUM")


def _stringify(value: Any, default: str = "") -> str:
    """Converts a value to string while handling None safely."""
    if value is None:
        return default
    return str(value)


def _collect_list(payload: Any, keys: Iterable[str]) -> list[dict[str, Any]]:
    """Collects the first matching list from a scan payload."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def parse_scan_results(raw_results: Any) -> list[Finding]:
    """Parses Gitleaks, Trivy, or Semgrep outputs into normalized findings."""
    if isinstance(raw_results, str):
        raise ValueError("Raw results must be loaded JSON, not a string")

    findings: list[Finding] = []
    if isinstance(raw_results, dict):
        if any(key in raw_results for key in ("Leaks", "leaks")):
            findings.extend(_parse_gitleaks(raw_results))

        trivy_results = [result for result in _collect_list(raw_results, ("Results", "results")) if _looks_like_trivy_result(result)]
        if trivy_results:
            findings.extend(_parse_trivy({"Results": trivy_results}))

        semgrep_results = [result for result in _collect_list(raw_results, ("results",)) if _looks_like_semgrep_result(result)]
        if semgrep_results:
            findings.extend(_parse_semgrep({"results": semgrep_results}))

    elif isinstance(raw_results, list):
        findings.extend(_parse_semgrep({"results": raw_results}))

    return findings


def _looks_like_trivy_result(result: dict[str, Any]) -> bool:
    """Detects Trivy result payloads."""
    vulnerabilities = result.get("Vulnerabilities") or result.get("vulnerabilities")
    return isinstance(vulnerabilities, list)


def _looks_like_semgrep_result(result: dict[str, Any]) -> bool:
    """Detects Semgrep result payloads."""
    return any(key in result for key in ("check_id", "checkId", "extra", "path", "start"))


def _parse_gitleaks(payload: dict[str, Any]) -> list[Finding]:
    """Parses Gitleaks leak findings."""
    findings: list[Finding] = []
    for item in _collect_list(payload, ("Leaks", "leaks")):
        file_name = _stringify(item.get("File") or item.get("file") or item.get("Path") or item.get("path"), "unknown")
        rule_id = _stringify(item.get("RuleID") or item.get("ruleId") or item.get("rule_id"), "gitleaks")
        message = _stringify(item.get("Description") or item.get("description") or item.get("Message") or item.get("message"), "Potential secret detected")
        severity = _normalize_severity(_stringify(item.get("Severity") or item.get("severity"), "high"))
        line_number = item.get("StartLine") or item.get("line") or item.get("lineNumber")
        findings.append(
            Finding(
                source_tool="Gitleaks",
                file_name=file_name,
                issue_type=rule_id,
                severity=severity,
                message=message,
                line_number=int(line_number) if isinstance(line_number, (int, str)) and str(line_number).isdigit() else None,
                raw=item,
            )
        )
    return findings


def _parse_trivy(payload: dict[str, Any]) -> list[Finding]:
    """Parses Trivy vulnerability findings."""
    findings: list[Finding] = []
    for result in _collect_list(payload, ("Results", "results")):
        target = _stringify(result.get("Target") or result.get("target"), "unknown")
        for vulnerability in _collect_list(result, ("Vulnerabilities", "vulnerabilities")):
            package = _stringify(vulnerability.get("PkgName") or vulnerability.get("pkgName") or vulnerability.get("packageName"), "package")
            vuln_id = _stringify(vulnerability.get("VulnerabilityID") or vulnerability.get("vulnerabilityId") or vulnerability.get("VulnerabilityId"), "trivy-vuln")
            title = _stringify(vulnerability.get("Title") or vulnerability.get("title") or vulnerability.get("Description"), "Vulnerability found")
            severity = _normalize_severity(_stringify(vulnerability.get("Severity") or vulnerability.get("severity"), "medium"))
            findings.append(
                Finding(
                    source_tool="Trivy",
                    file_name=target,
                    issue_type=f"{package}:{vuln_id}",
                    severity=severity,
                    message=title,
                    line_number=None,
                    raw=vulnerability,
                )
            )
    return findings


def _parse_semgrep(payload: dict[str, Any]) -> list[Finding]:
    """Parses Semgrep rule findings."""
    findings: list[Finding] = []
    for item in _collect_list(payload, ("results", "Results")):
        path = item.get("path") or item.get("file") or item.get("filename") or "unknown"
        check_id = _stringify(item.get("check_id") or item.get("checkId") or item.get("rule_id") or item.get("ruleId"), "semgrep-rule")
        extra = item.get("extra") if isinstance(item.get("extra"), dict) else {}
        message = _stringify(extra.get("message") or item.get("message") or item.get("msg"), "Potential insecure pattern detected")
        severity = _normalize_severity(_stringify(extra.get("severity") or item.get("severity"), "medium"))
        line_number = item.get("start") or item.get("line") or item.get("lineNumber")
        if isinstance(line_number, dict):
            line_number = line_number.get("line")
        findings.append(
            Finding(
                source_tool="Semgrep",
                file_name=_stringify(path, "unknown"),
                issue_type=check_id,
                severity=severity,
                message=message,
                line_number=int(line_number) if isinstance(line_number, (int, str)) and str(line_number).isdigit() else None,
                raw=item,
            )
        )
    return findings
