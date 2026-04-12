"""LLM analysis logic using LangChain and Ollama."""

from __future__ import annotations

import json
import logging
from typing import Any

import requests

from devsecops_agent.config import settings
from devsecops_agent.models import AnalysisResult, Finding

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict[str, Any]:
    """Extracts a JSON object from raw LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response did not contain JSON")
    return json.loads(cleaned[start : end + 1])


def analyze_finding(finding: Finding) -> AnalysisResult:
    """Analyzes a single normalized finding using the local Ollama model."""
    try:
        payload = _analyze_with_ollama_http(finding)
        return AnalysisResult.model_validate(payload)
    except Exception as exc:  # pragma: no cover - used when Ollama is unavailable
        logger.warning("Falling back to heuristic analysis for %s: %s", finding.file_name, exc)
        return _heuristic_analysis(finding)


def analyze_findings(findings: list[Finding]) -> list[AnalysisResult]:
    """Analyzes a list of findings and returns structured results."""
    return [analyze_finding(finding) for finding in findings]


def _heuristic_analysis(finding: Finding) -> AnalysisResult:
    """Builds a deterministic analysis when the local LLM is unavailable."""
    issue = f"{finding.issue_type} in {finding.file_name}"
    severity = finding.severity if finding.severity in {"LOW", "MEDIUM", "HIGH"} else "MEDIUM"

    risk_map = {
        "LOW": "Limited exposure, but still worth fixing before it spreads or gets reused.",
        "MEDIUM": "Could be exploited under realistic conditions and may lead to privilege or data exposure.",
        "HIGH": "Likely exploitable and could result in secret leakage, compromise, or sensitive data exposure.",
    }

    fix_map = {
        "Gitleaks": "Remove the secret from source control, rotate the exposed credential, and move secrets to a vault or environment variable.",
        "Trivy": "Upgrade the affected dependency or base image to a patched version and rebuild the artifact.",
        "Semgrep": "Refactor the code to follow the secure pattern, then add validation or a safer API call.",
    }

    return AnalysisResult(
        issue=issue,
        severity=severity,
        risk=risk_map[severity],
        fix=fix_map.get(finding.source_tool, "Apply the security best practice for this finding and verify the issue is no longer detected."),
        confidence=0.72 if severity == "HIGH" else 0.67 if severity == "MEDIUM" else 0.61,
    )


def _analyze_with_ollama_http(finding: Finding) -> dict[str, Any]:
    """Calls the local Ollama HTTP API directly and returns parsed JSON."""
    prompt = (
        "You are a senior DevSecOps assistant. Analyze a single security finding and respond only with valid JSON matching this schema: "
        '{"issue": string, "severity": "LOW"|"MEDIUM"|"HIGH", "risk": string, "fix": string, "confidence": number}. '
        "Keep the response concise, practical, and implementation-focused.\n\n"
        f"Tool: {finding.source_tool}\n"
        f"File: {finding.file_name}\n"
        f"Issue type: {finding.issue_type}\n"
        f"Scanner severity: {finding.severity}\n"
        f"Message: {finding.message}\n"
        f"Line: {finding.line_number if finding.line_number is not None else 'unknown'}\n\n"
        "Rules:\n"
        "1. Explain the vulnerability in plain language.\n"
        "2. Classify severity as LOW, MEDIUM, or HIGH.\n"
        "3. Suggest a concrete fix.\n"
        "4. Provide confidence as a float from 0.0 to 1.0.\n"
        "5. Return JSON only."
    )

    response = requests.post(
        f"{settings.ollama_base_url.rstrip('/')}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json().get("response", "")
    return _extract_json(content)
