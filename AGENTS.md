# AGENTS.md — Scrapling & Ecosystem Knowledge

Operational guidelines, architecture context, and strict invariants for AI coding agents (`agy`, Claude Code, Codex) working within the **`Scrapling`** codebase and its companion **SSO Ecosystem**.

---

## 1. Project Overview & Role

- **Repository**: `common/Scrapling` (Core Engine & MCP Server)
- **Primary Role**: High-performance, undetectable, adaptive web scraping engine in Python 3.12.
- **Companion Projects**:
  - **`scrapling-studio`** (`../../2agents/scrapling-studio`): Visual scraper cockpit (Next.js 16 on `:3060`) and headless spider orchestrator (FastAPI on `:8060`, SQLite `studio.db`, Portainer Stack 23).
  - **`sso-brain`** (`../../sso-brain`): Central ecosystem AST knowledge gateway, WebGL architecture graph, and cross-repo dependency registry (Port `:8025`).
- **Built-in MCP Server**: Native FastMCP endpoint running at `127.0.0.1:8000` (`uv run scrapling mcp --http --host 127.0.0.1 --port 8000 --no-auth`).

---

## 2. Core Architecture & Fetcher Modes

Scrapling provides three complementary fetching tiers designed for speed, dynamic rendering, and anti-bot bypass:

1. **`Fetcher` (`scrapling.core.fetcher`)**:
   - HTTP/1.1 & HTTP/2 TLS impersonation engine built on `curl_cffi`.
   - Mimics real browser TLS signatures (JA3/JA4) with zero headless browser overhead.
   - Recommended for static sites, public REST APIs, and high-throughput bulk crawls.
2. **`DynamicFetcher` (`scrapling.core.dynamic`)**:
   - Headless Chromium automation powered by Playwright.
   - Renders JavaScript-heavy Single Page Applications (SPAs), waits for dynamic selectors, and executes DOM scripts.
3. **`StealthyFetcher` (`scrapling.core.stealthy`)**:
   - Anti-fingerprinting browser engine powered by Patchright / Camoufox.
   - Automatically bypasses Cloudflare Turnstile, browser integrity checks, and canvas fingerprinting.

### RAG & Clean Markdown Integration
- Built-in `--ai-targeted` flag strips boilerplate (navigation, footer, ads) and transforms clean DOM subtrees directly into markdown optimized for LLM context windows.

---

## 3. Essential Commands & Development Workflow

### Python Environment (`uv`)
Always use `uv` inside `.venv`. **Never run global `pip install`**.
```bash
# Setup environment
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[all]"

# Run tests
uv run pytest tests/parser/ tests/core/ -q  # Smoke tests
uv run pytest tests/                        # Full test suite

# Code quality
uv run ruff check .
uv run ruff format .

# Launch local MCP server daemon
uv run scrapling mcp --http --host 127.0.0.1 --port 8000 --no-auth
```

### CLI Quick Scrapes
```bash
# Fast HTTP TLS crawl to clean Markdown
uv run scrapling extract get "https://quotes.toscrape.com/" output.md --ai-targeted

# Stealth crawl with Cloudflare Turnstile solver
uv run scrapling extract stealthy-fetch "<URL>" output.md --solve-cloudflare --ai-targeted
```

---

## 4. Port Reservation & Ecosystem Matrix (Strict Invariant)

All AI agents across the ecosystem MUST strictly observe established port allocations. **NEVER hijack, bind to, or terminate an existing assigned port**:

| Port(s) | Service | Location / Description |
| :--- | :--- | :--- |
| `3000`, `3004` | `sso-service` | Central Identity / OIDC Auth Provider (Stack 16) |
| `3001` | `sso-admin` | Control Plane & BFF (Next.js 15) |
| `3002` | `wallet-service` | Financial Ledger & Wallet Engine |
| `3003` | `event-service` | Distributed Event Broker |
| `3030` | `s8-service` | Security Policy Enforcer |
| `3050` | `tts-voice-studio` | Trilingual AI Voice Studio |
| `3060` | `scrapling-studio-frontend` | Scrapling Studio Cockpit (Next.js 16, Stack 23) |
| `4000`, `5173` | `here-iam` | Identity Presence & Social Gateway |
| `4001` | `log-service` | Central Structured Logging Gateway |
| `4320`-`4322`, `8020`-`8022` | `sso-develop` | Docs, Help Center & Legal Suites |
| `7000` | `lika-tunnel` | Ingress Proxy & Edge Routing |
| `7001` | `tcp-service` | TCP Gateway Engine |
| `8000` | `scrapling-mcp` | Scrapling Native MCP Server (Python FastMCP) |
| `8008`-`8010` | `vaultstream` | Media Streaming, Scraper & API Suite (Stack 18) |
| `8024` | `me555` | Operator Docker API Proxy & Launchpad (Stack 22) |
| `8025` | `sso-brain` | Central Ecosystem Knowledge Gateway & AST Explorer |
| `8026` | `laya` | System 1 Fast Decision & Guardrail Engine |
| `8030`-`8032` | `bookstore` | Bookstore E-Commerce Engine & Storefront (Stack 21) |
| `8060` | `scrapling-studio-backend` | Scrapling Studio Spider API (FastAPI, Stack 23) |
| `11434` | `ollama` | Local LLM Inference Engine |
| `18789` | `openclaw` | Autonomous Crawler Daemon |

*Always run `lsof -iTCP:<PORT> -sTCP:LISTEN -P -n` before launching any dev server.*

---

## 5. Non-Negotiable Agent Rules

1. **Git Commit Message Rule**:
   - Strictly ONE short, sharp line in imperative mood, ≤ 72 characters (e.g. `feat(scope): concise description` or `fix(scope): concise description`).
   - Strictly NO commit body, NO bullet lists, NO `Co-Authored-By`, NO metadata trailers.
2. **Local Service Reporting Format**:
   - When reporting running services across any ecosystem repository or brain:
   - **NEVER** include a `Description` column.
   - Use strictly concise columns: `| Service | Local URL | Status |`.
3. **Zero Contact / Domain Leaks**:
   - **NEVER** embed developer personal emails, phone numbers, personal contacts, or private production domain references into repository files, workflows, or documentation.
4. **Preserve Comments & Docstrings**:
   - Preserve all existing comments and docstrings unrelated to current code edits.
5. **UI Dropdown & Selection Invariant**:
   - NEVER use unstyled native HTML `<select>` elements in toolbars or filters (they overlap adjacent UI elements on macOS/Chromium/Safari).
   - Strictly use anchored custom popovers (`CustomSelect`) with `top-full mt-1.5` / `bottom-full mb-1.5`, `z-50`, and click-outside dismissal.
6. **Trilingual Localization Invariant (English, Khmer, Chinese)**:
   - Any UI developed or modified for Scrapling Studio (`scrapling-studio/frontend`) MUST be translated across **English (`en`)**, **Khmer (`km`)**, and **Chinese (`zh`)** via `frontend/src/i18n/translations.ts` and `useTranslation()`.
   - Never leave hardcoded English strings in UI components. All newly added pages, modals, or controls must declare translations in all three languages.


