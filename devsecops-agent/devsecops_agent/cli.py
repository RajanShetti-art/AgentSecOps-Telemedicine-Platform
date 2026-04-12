"""Command-line entry point for the DevSecOps agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from devsecops_agent.models import AnalysisResult, CommentTarget
from devsecops_agent.service import analyze_scan_results, post_analysis_to_pull_request


def _load_input(path: str) -> Any:
    """Loads raw scan results from a file or standard input."""
    if path == "-":
        return json.loads(input())
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _build_parser() -> argparse.ArgumentParser:
    """Builds the command-line argument parser."""
    parser = argparse.ArgumentParser(description="AI DevSecOps agent for scan result analysis")
    parser.add_argument("--input", required=True, help="Path to scan results JSON file or - for stdin")
    parser.add_argument("--post-github-comments", action="store_true", help="Post analysis as GitHub PR comments")
    parser.add_argument("--github-owner", help="GitHub repository owner")
    parser.add_argument("--github-repo", help="GitHub repository name")
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument("--github-token", help="GitHub token; defaults to GITHUB_TOKEN env var")
    return parser


def main() -> None:
    """Runs the CLI workflow for parsing, analysis, and optional PR commenting."""
    args = _build_parser().parse_args()
    raw_results = _load_input(args.input)
    findings, analyses = analyze_scan_results(raw_results)

    output = [analysis.model_dump() for analysis in analyses]
    print(json.dumps(output, indent=2))

    if args.post_github_comments:
        if not all([args.github_owner, args.github_repo, args.pr_number]):
            raise SystemExit("--github-owner, --github-repo, and --pr-number are required when posting comments")
        from devsecops_agent.config import settings

        token = args.github_token or settings.github_token
        if not token:
            raise SystemExit("GitHub token is required via --github-token or GITHUB_TOKEN")

        target = CommentTarget(owner=args.github_owner, repo=args.github_repo, pull_number=args.pr_number)
        post_analysis_to_pull_request(target, token, findings, analyses)


if __name__ == "__main__":
    main()
