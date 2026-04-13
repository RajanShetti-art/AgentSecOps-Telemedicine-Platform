"""GitHub PR comment integration helpers."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def format_comment(result: dict[str, Any]) -> str:
    """Formats one analysis result into markdown for PR comments."""
    return (
        f"### DevSecOps Finding: {result.get('issue', 'Unknown')}\n\n"
        f"- **File:** {result.get('file', 'unknown')}\n"
        f"- **Severity:** {result.get('severity', 'MEDIUM')}\n"
        f"- **Risk:** {result.get('risk', '')}\n"
        f"- **Fix:** {result.get('fix', '')}\n"
        f"- **Confidence:** {float(result.get('confidence', 0.0)):.2f}\n"
    )


def post_pr_comment(owner: str, repo: str, pr_number: int, github_token: str, body: str) -> dict[str, Any]:
    """Posts a single issue comment to a GitHub pull request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": body},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def post_results_to_pr(
    owner: str,
    repo: str,
    pr_number: int,
    github_token: str,
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Posts all analysis results as individual pull request comments."""
    posted: list[dict[str, Any]] = []

    for result in results:
        try:
            posted.append(post_pr_comment(owner, repo, pr_number, github_token, format_comment(result)))
        except Exception as exc:
            logger.exception("Failed to post PR comment for %s: %s", result.get("file", "unknown"), exc)

    return posted
