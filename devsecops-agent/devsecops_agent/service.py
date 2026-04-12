"""Orchestration service for security scan analysis."""

from __future__ import annotations

from typing import Any

from devsecops_agent.analyzer import analyze_findings
from devsecops_agent.github_client import build_pr_comment_body, post_pr_comment
from devsecops_agent.models import AnalysisResult, CommentTarget, Finding
from devsecops_agent.parser import parse_scan_results


def analyze_scan_results(raw_results: Any) -> tuple[list[Finding], list[AnalysisResult]]:
    """Parses raw scan results and analyzes each finding."""
    findings = parse_scan_results(raw_results)
    analyses = analyze_findings(findings) if findings else []
    return findings, analyses


def post_analysis_to_pull_request(
    target: CommentTarget,
    token: str,
    findings: list[Finding],
    analyses: list[AnalysisResult],
) -> list[dict[str, Any]]:
    """Posts one GitHub PR comment per analyzed finding."""
    comments: list[dict[str, Any]] = []
    for finding, analysis in zip(findings, analyses, strict=True):
        comment_body = build_pr_comment_body(finding, analysis)
        comments.append(post_pr_comment(target, token, comment_body))
    return comments
