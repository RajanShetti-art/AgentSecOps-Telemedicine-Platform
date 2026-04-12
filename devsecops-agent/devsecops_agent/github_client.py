"""GitHub API helpers for commenting on pull requests."""

from __future__ import annotations

from typing import Any

import requests

from devsecops_agent.models import AnalysisResult, CommentTarget, Finding

_GITHUB_API_BASE = "https://api.github.com"


def build_pr_comment_body(finding: Finding, analysis: AnalysisResult) -> str:
    """Builds a markdown comment body for a pull request."""
    location = finding.file_name
    if finding.line_number is not None:
        location = f"{location}:{finding.line_number}"

    return (
        f"### Security Finding: {analysis.issue}\n\n"
        f"- **Tool:** {finding.source_tool}\n"
        f"- **File:** {location}\n"
        f"- **Severity:** {analysis.severity}\n"
        f"- **Risk:** {analysis.risk}\n"
        f"- **Fix:** {analysis.fix}\n"
        f"- **Confidence:** {analysis.confidence:.2f}\n"
    )


def post_pr_comment(target: CommentTarget, token: str, body: str) -> dict[str, Any]:
    """Posts a comment to a GitHub pull request using the GitHub API."""
    url = f"{_GITHUB_API_BASE}/repos/{target.owner}/{target.repo}/issues/{target.pull_number}/comments"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": body},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
