# agentgif

[![PyPI](https://img.shields.io/pypi/v/agentgif)](https://pypi.org/project/agentgif/)
[![Python](https://img.shields.io/pypi/pyversions/agentgif)](https://pypi.org/project/agentgif/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![AgentGIF Badge](https://agentgif.com/badge/pypi/agentgif/version.svg?theme=dracula)](https://agentgif.com/docs/cli/)

**CLI for [AgentGIF](https://agentgif.com) — upload, manage, and share terminal GIFs from the command line.**

[AgentGIF](https://agentgif.com) is a developer GIF hosting platform built for terminal recordings. Upload GIFs with asciicast files for interactive replay, generate terminal-themed package badges, and share your command-line demos with embed codes for GitHub READMEs, blogs, and documentation. Built with Python ([click](https://click.palletsprojects.com/) + [httpx](https://www.python-httpx.org/) + [rich](https://rich.readthedocs.io/)).

> **Try it live at [agentgif.com](https://agentgif.com)** — [Explore GIFs](https://agentgif.com/explore/) | [Badge Generator](https://agentgif.com/docs/cli/) | [Upload](https://agentgif.com/upload/)

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do with AgentGIF](#what-you-can-do-with-agentgif)
  - [Upload and Share Terminal GIFs](#upload-and-share-terminal-gifs)
  - [Terminal Cast Replay with Themes](#terminal-cast-replay-with-themes)
  - [Terminal-Themed Package Badges](#terminal-themed-package-badges)
  - [AI Tape Generator](#ai-tape-generator)
  - [Collections and Tags](#collections-and-tags)
  - [Search and Embed](#search-and-embed)
- [Commands](#commands)
  - [Authentication](#authentication)
  - [GIF Management](#gif-management)
  - [Badge Service](#badge-service)
- [Configuration](#configuration)
- [Also Available](#also-available)
- [Learn More About AgentGIF](#learn-more-about-agentgif)
- [License](#license)

## Install

```bash
pip install agentgif
```

Requires Python 3.10+.

## Quick Start

```bash
# Authenticate via browser (device flow)
agentgif login

# Upload a GIF with metadata
agentgif upload demo.gif --title "Docker Build" --command "docker compose up"

# Record a VHS tape and upload the resulting GIF
agentgif record my-tape.tape

# Search public terminal GIFs
agentgif search "git rebase"

# Generate embed codes for a GIF
agentgif embed abc12345

# Generate a terminal-themed badge for your package
agentgif badge url -p pypi -k agentgif --theme dracula
```

## What You Can Do with AgentGIF

### Upload and Share Terminal GIFs

[AgentGIF](https://agentgif.com) hosts GIFs specifically designed for developer workflows. Upload terminal recordings from tools like [asciinema](https://asciinema.org), [VHS](https://github.com/charmbracelet/vhs), or screen capture. Each upload accepts optional metadata — title, description, the command being demonstrated, tags, and the repository it belongs to. GIFs are served from a global CDN at `media.agentgif.com` for fast embedding anywhere.

```bash
# Upload with full metadata
agentgif upload demo.gif \
  --title "Running pytest with coverage" \
  --description "Full test suite with branch coverage report" \
  --command "pytest --cov=src --cov-report=term-missing" \
  --tags "python,testing,pytest,coverage"

# Upload with an asciicast file for interactive replay
agentgif upload demo.gif --cast demo.cast --theme monokai
```

When you include a `.cast` asciicast file alongside your GIF, AgentGIF provides [interactive terminal replay](https://agentgif.com/explore/) — viewers can see the exact keystrokes, timing, and output as if they were watching the terminal live. Choose from 15 terminal themes including Dracula, Monokai, Solarized Dark, Nord, and Catppuccin.

Learn more: [Upload a GIF](https://agentgif.com/upload/) · [Explore Terminal GIFs](https://agentgif.com/explore/)

### Terminal Cast Replay with Themes

Every GIF on AgentGIF can optionally include an asciicast recording for frame-by-frame terminal replay. The cast player supports 15 built-in terminal themes that match popular developer environments:

| Theme | Style | Best For |
|-------|-------|----------|
| Dracula | Purple-toned dark | General-purpose, high contrast |
| Monokai | Warm dark | Code demos, syntax-heavy output |
| Solarized Dark | Blue-green dark | Long-form terminal sessions |
| Nord | Cool blue dark | Minimal, distraction-free |
| Catppuccin Mocha | Pastel dark | Modern developer aesthetic |
| One Dark | Atom-inspired dark | Familiar to VS Code users |
| Tokyo Night | Deep purple dark | Japanese-inspired minimalism |
| Gruvbox Dark | Retro warm dark | Vim/Neovim workflows |

```bash
# Upload with a specific terminal theme
agentgif upload demo.gif --cast demo.cast --theme dracula

# List all available themes
agentgif badge themes
```

Learn more: [Terminal Themes](https://agentgif.com/themes/) · [Explore GIFs](https://agentgif.com/explore/)

### Terminal-Themed Package Badges

AgentGIF provides a [terminal-themed badge service](https://agentgif.com/docs/cli/) — a developer-native alternative to shields.io. Badges render as SVGs styled like terminal prompts, fetching live data from PyPI, npm, crates.io, and GitHub.

```bash
# PyPI version badge
agentgif badge url -p pypi -k flask
# → https://agentgif.com/badge/pypi/flask/version.svg

# npm version badge with Dracula theme
agentgif badge url -p npm -k react --theme dracula
# → https://agentgif.com/badge/npm/react/version.svg?theme=dracula

# crates.io version badge
agentgif badge url -p crates -k serde
# → https://agentgif.com/badge/crates/serde/version.svg

# GitHub stars badge
agentgif badge url -p github -k "vercel/next.js" -m stars
# → https://agentgif.com/badge/github/vercel/next.js/stars.svg

# Get Markdown embed code
agentgif badge url -p pypi -k django --format md
# → [![PyPI Version](https://agentgif.com/badge/pypi/django/version.svg)](https://pypi.org/project/django/)
```

**Providers:** `pypi`, `npm`, `crates`, `github`
**Metrics:** `version` (default), `downloads`, `stars`
**Themes:** All 15 terminal themes — `dracula`, `monokai`, `catppuccin-mocha`, `nord`, `solarized-dark`, etc.
**Styles:** `default` (terminal prompt), `flat`

Learn more: [Badge Generator](https://agentgif.com/docs/cli/) · [Badge Documentation](https://agentgif.com/docs/cli/)

### AI Tape Generator

The `generate` command leverages AI to automatically create [VHS tape files](https://github.com/charmbracelet/vhs) from any GitHub repository. Point it at a repo and AgentGIF analyzes the README, package manifests, and source code to produce realistic terminal demo recordings.

```bash
# Generate terminal demo GIFs from a GitHub repository
agentgif generate https://github.com/psf/requests

# Check generation status
agentgif generate-status <job-id>
```

The AI pipeline extracts interesting commands (install, test, usage examples), generates VHS tape scripts with realistic mock outputs, records them, and uploads the resulting GIFs — all automatically.

Learn more: [AI Tape Generator](https://agentgif.com/generate/) · [API Documentation](https://agentgif.com/docs/api/)

### Collections and Tags

Organize GIFs into [collections](https://agentgif.com/collections/) — curated groups of related terminal recordings. Tag GIFs with descriptive labels for easy discovery.

```bash
# List your GIFs filtered by repository
agentgif list --repo "myorg/myrepo"

# View all tags on a GIF
agentgif info abc12345
```

Browse public collections at [agentgif.com/collections/](https://agentgif.com/collections/).

Learn more: [Collections](https://agentgif.com/collections/) · [Explore GIFs](https://agentgif.com/explore/)

### Search and Embed

Find terminal GIFs across the platform with full-text search. Every GIF comes with ready-to-use embed codes for Markdown, HTML, iframes, and script tags.

```bash
# Search for Docker-related terminal GIFs
agentgif search "docker compose"

# Get embed codes in all formats
agentgif embed abc12345

# Get only the Markdown embed
agentgif embed abc12345 --format md
```

Embed formats include:
- **Markdown** — `![title](url)` for GitHub READMEs
- **HTML** — `<img>` tag for websites
- **iframe** — Full cast player with replay controls
- **Script** — JavaScript widget for interactive embedding

Learn more: [Search GIFs](https://agentgif.com/explore/) · [Embed Documentation](https://agentgif.com/docs/cli/)

## Commands

### Authentication

```bash
agentgif login          # Open browser to authenticate (device flow)
agentgif logout         # Remove stored credentials
agentgif whoami         # Show current user info
```

### GIF Management

```bash
agentgif upload <gif>   # Upload a GIF
  -t, --title <title>       GIF title
  -d, --description <desc>  Description
  -c, --command <cmd>        Command demonstrated
  --tags <tags>              Comma-separated tags
  --cast <path>              Asciicast file for interactive replay
  --theme <theme>            Terminal theme (dracula, monokai, nord, etc.)
  --unlisted                 Upload as unlisted
  --no-repo                  Don't auto-detect git repository

agentgif record <tape>    # Run VHS tape → upload resulting GIF
agentgif search <query>   # Search public GIFs
agentgif list             # List your GIFs
  --repo <repo>              Filter by repository slug

agentgif info <gifId>     # Show GIF details (JSON)
agentgif embed <gifId>    # Show embed codes
  -f, --format <fmt>         md, html, iframe, script, all

agentgif update <gifId>   # Update GIF metadata
  -t, --title <title>       New title
  -d, --description <desc>  New description
  -c, --command <cmd>        New command
  --tags <tags>              New tags

agentgif delete <gifId>   # Delete a GIF
  -y, --yes                  Skip confirmation

agentgif generate <url>         # AI-generate terminal demo GIFs from a GitHub repo
agentgif generate-status <id>   # Check generation job status
```

### Badge Service

```bash
agentgif badge url        # Generate badge URL + embed codes
  -p, --provider <p>        pypi, npm, crates, github
  -k, --package <pkg>       Package name (or owner/repo for GitHub)
  -m, --metric <m>          version, downloads, stars (default: version)
  --theme <theme>            Terminal theme (e.g. dracula, monokai)
  --style <style>            Badge style (default, flat)
  -f, --format <fmt>         url, md, html, img, all

agentgif badge themes     # List all available terminal themes
```

## Configuration

Credentials are stored at `~/.config/agentgif/config.json`.

The CLI authenticates via GitHub OAuth device flow — run `agentgif login` and approve in your browser. The token is stored locally and used for all authenticated API calls.

## Also Available

The AgentGIF CLI is available in 5 languages. Use whichever fits your toolchain:

| Language | Package | Install | Source |
|----------|---------|---------|--------|
| **Python** | [PyPI](https://pypi.org/project/agentgif/) | `pip install agentgif` | [agentgif-python](https://github.com/dobestan/agentgif-python) |
| Node.js | [npm](https://www.npmjs.com/package/agentgif) | `npm install -g agentgif` | [agentgif-node](https://github.com/dobestan/agentgif-node) |
| Rust | [crates.io](https://crates.io/crates/agentgif) | `cargo install agentgif` | [agentgif-rust](https://github.com/dobestan/agentgif-rust) |
| Ruby | [RubyGems](https://rubygems.org/gems/agentgif) | `gem install agentgif` | [agentgif-ruby](https://github.com/dobestan/agentgif-ruby) |
| Go | [pkg.go.dev](https://pkg.go.dev/github.com/dobestan/agentgif-go) | `go install github.com/dobestan/agentgif-go@latest` | [agentgif-go](https://github.com/dobestan/agentgif-go) |

All implementations share the same command interface and API.

## Learn More About AgentGIF

- **Platform**: [agentgif.com](https://agentgif.com) — Developer GIF hosting for terminal recordings
- **Explore**: [Browse Terminal GIFs](https://agentgif.com/explore/) · [Collections](https://agentgif.com/collections/) · [Tags](https://agentgif.com/collections/)
- **Tools**: [Badge Generator](https://agentgif.com/docs/cli/) · [AI Tape Generator](https://agentgif.com/generate/) · [Upload](https://agentgif.com/upload/)
- **Search**: [Search GIFs](https://agentgif.com/explore/) · [Terminal Themes](https://agentgif.com/themes/)
- **Docs**: [CLI Documentation](https://agentgif.com/docs/cli/) · [API Reference](https://agentgif.com/docs/api/)

## License

MIT
