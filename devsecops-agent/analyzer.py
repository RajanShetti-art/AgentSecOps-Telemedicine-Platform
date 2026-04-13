"""LangChain + Ollama analyzer for DevSecOps findings."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a DevSecOps security reviewer. Return JSON only with keys: file, issue, severity, risk, fix, confidence. Severity must be LOW, MEDIUM, or HIGH. Confidence must be a float between 0 and 1.",
        ),
        (
            "human",
            "Analyze this issue:\n"
            "file: {file}\n"
            "issue: {issue}\n"
            "severity_from_scanner: {severity}\n"
            "message: {message}\n"
            "tool: {tool}\n\n"
            "Tasks:\n"
            "1) Explain vulnerability clearly in risk.\n"
            "2) Classify severity as LOW/MEDIUM/HIGH.\n"
            "3) Suggest concrete fix.\n"
            "4) Provide confidence in [0,1].\n"
            "5) Return JSON only.",
        ),
    ]
)


class DevSecOpsAnalyzer:
    """Analyzes security findings with Ollama through LangChain."""

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        """Initializes a LangChain chat model for Ollama."""
        self.model_name = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = ChatOllama(model=self.model_name, base_url=self.base_url, temperature=0.2)

    def analyze_issue(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Analyzes a single finding and returns normalized output schema."""
        try:
            chain = _PROMPT | self.llm
            response = chain.invoke(issue)
            raw = getattr(response, "content", str(response))
            parsed = _extract_json(raw)
            return _normalize_output(parsed, issue)
        except Exception as exc:
            logger.exception("LLM analysis failed for %s: %s", issue.get("file", "unknown"), exc)
            return _fallback_output(issue)

    def analyze_issues(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Analyzes all findings and returns structured output list."""
        return [self.analyze_issue(item) for item in issues]


def _extract_json(text: str) -> dict[str, Any]:
    """Extracts and parses JSON from model response text."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response")

    return json.loads(cleaned[start : end + 1])


def _normalize_output(parsed: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    """Ensures final output strictly matches required schema."""
    severity = str(parsed.get("severity") or source.get("severity") or "MEDIUM").upper()
    if severity not in {"LOW", "MEDIUM", "HIGH"}:
        severity = "MEDIUM"

    confidence = parsed.get("confidence", 0.6)
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.6
    confidence = max(0.0, min(1.0, confidence))

    return {
        "file": str(parsed.get("file") or source.get("file") or "unknown"),
        "issue": str(parsed.get("issue") or source.get("issue") or "unknown issue"),
        "severity": severity,
        "risk": str(parsed.get("risk") or "Potential security impact requires remediation."),
        "fix": str(parsed.get("fix") or "Apply secure coding best practices and rerun scans."),
        "confidence": confidence,
    }


def _fallback_output(source: dict[str, Any]) -> dict[str, Any]:
    """Provides deterministic output when LLM call fails."""
    severity = str(source.get("severity") or "MEDIUM").upper()
    if severity not in {"LOW", "MEDIUM", "HIGH"}:
        severity = "MEDIUM"

    risk_map = {
        "LOW": "Limited immediate impact, but unresolved findings can accumulate risk.",
        "MEDIUM": "Can lead to exploitable weaknesses under common deployment conditions.",
        "HIGH": "Likely exploitable and may expose secrets, data, or system integrity.",
    }

    fix_map = {
        "Gitleaks": "Remove exposed secret, rotate credentials, and use a secrets manager.",
        "Trivy": "Upgrade vulnerable dependency or base image and rebuild artifacts.",
        "Semgrep": "Refactor insecure code pattern and add validation or safer APIs.",
    }

    return {
        "file": str(source.get("file") or "unknown"),
        "issue": str(source.get("issue") or "unknown issue"),
        "severity": severity,
        "risk": risk_map[severity],
        "fix": fix_map.get(str(source.get("tool") or ""), "Apply secure coding fixes and verify with rescans."),
        "confidence": 0.7 if severity == "HIGH" else 0.65 if severity == "MEDIUM" else 0.6,
    }
