"""Entry point for AI DevSecOps agent workflow."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

from analyzer import DevSecOpsAnalyzer
from github import post_results_to_pr
from parser import parse_scan_results


def configure_logging() -> None:
    """Configures root logger for structured runtime visibility."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def load_json(path: str) -> Any:
    """Loads JSON scan payload from a file path."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_arg_parser() -> argparse.ArgumentParser:
    """Builds command-line arguments for the agent workflow."""
    parser = argparse.ArgumentParser(description="AI DevSecOps Agent")
    parser.add_argument("--input", required=True, help="Path to JSON scan results")
    parser.add_argument("--ollama-model", default=os.getenv("OLLAMA_MODEL", "llama3"), help="Ollama model name")
    parser.add_argument("--ollama-base-url", default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), help="Ollama base URL")
    parser.add_argument("--post-pr-comment", action="store_true", help="Post analysis results as PR comments")
    parser.add_argument("--github-owner", default=os.getenv("GITHUB_REPO_OWNER", ""), help="GitHub repository owner")
    parser.add_argument("--github-repo", default=os.getenv("GITHUB_REPO_NAME", ""), help="GitHub repository name")
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument("--github-token", default=os.getenv("GITHUB_TOKEN", ""), help="GitHub token")
    return parser


def run() -> int:
    """Runs the end-to-end parse, analyze, and optional PR comment workflow."""
    configure_logging()
    args = build_arg_parser().parse_args()
    logger = logging.getLogger("devsecops-agent")

    try:
        raw = load_json(args.input)
        issues = parse_scan_results(raw)
        analyzer = DevSecOpsAnalyzer(model=args.ollama_model, base_url=args.ollama_base_url)
        results = analyzer.analyze_issues(issues)

        print(json.dumps(results, indent=2))

        if args.post_pr_comment:
            if not all([args.github_owner, args.github_repo, args.pr_number, args.github_token]):
                raise ValueError("GitHub owner/repo/pr-number/token are required for PR comments")

            post_results_to_pr(
                owner=args.github_owner,
                repo=args.github_repo,
                pr_number=args.pr_number,
                github_token=args.github_token,
                results=results,
            )

        return 0
    except Exception as exc:
        logger.exception("DevSecOps agent failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
