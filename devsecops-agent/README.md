# AI DevSecOps Agent

A modular Python agent that ingests security scan results from Gitleaks, Trivy, and Semgrep, normalizes findings, uses a local Ollama model through LangChain to analyze each issue, and can optionally post comments to GitHub pull requests.

## Features

- Parses scan results into normalized findings
- Explains the vulnerability
- Classifies severity as LOW, MEDIUM, or HIGH
- Suggests a fix
- Returns a confidence score
- Uses Ollama as the local LLM backend
- Posts GitHub PR comments through the GitHub API

## Structure

- `devsecops_agent/parser.py` normalizes scan findings
- `devsecops_agent/analyzer.py` runs the LangChain + Ollama analysis
- `devsecops_agent/github_client.py` posts PR comments
- `devsecops_agent/service.py` orchestrates parsing and analysis
- `devsecops_agent/cli.py` provides a command-line entry point

## Setup

```bash
cd devsecops-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Make sure Ollama is running locally and the model is available:

```bash
ollama pull llama3.1
ollama serve
```

## Run

Analyze a scan file:

```bash
python -m devsecops_agent.cli --input scan-results.json
```

Analyze and post comments to a GitHub PR:

```bash
python -m devsecops_agent.cli \
  --input scan-results.json \
  --post-github-comments \
  --github-owner RajanShetti-art \
  --github-repo AgentSecOps-Telemedicine-Platform \
  --pr-number 12
```

## Expected Input

The parser accepts common outputs from:

- Gitleaks
- Trivy
- Semgrep

The agent normalizes each finding to include:

- file name
- issue type
- severity
- message
- source tool

## Output Format

Each analysis result follows this structure:

```json
{
  "issue": "",
  "severity": "",
  "risk": "",
  "fix": "",
  "confidence": 0.0
}
```
