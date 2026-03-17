# agentgif

CLI for [AgentGIF](https://agentgif.com) — upload, manage, and share terminal GIFs.

**GIF for humans. Cast for agents.**

## Install

```bash
pip install agentgif
```

## Quick Start

```bash
# Authenticate via browser
agentgif login

# Upload a GIF
agentgif upload demo.gif --title "My Demo" --command "git commit"

# Record with VHS and upload
agentgif record my-tape.tape

# Search public GIFs
agentgif search "docker compose"

# Get embed codes
agentgif embed <gif-id>

# Generate a terminal-themed badge
agentgif badge url -p pypi -k colorfyi
```

## Commands

| Command | Description |
|---------|-------------|
| `login` | Authenticate via browser (device flow) |
| `logout` | Remove stored credentials |
| `whoami` | Show current user |
| `upload` | Upload a GIF (+ optional cast file) |
| `record` | Run VHS tape → upload GIF |
| `search` | Search public GIFs |
| `list` | List your GIFs |
| `info` | Show GIF details (JSON) |
| `embed` | Show embed codes |
| `update` | Update GIF metadata |
| `delete` | Delete a GIF |
| `badge url` | Generate a terminal-themed badge URL + embed codes |
| `badge themes` | List available terminal themes for badges |

### Badge Commands

```bash
# Generate badge for a PyPI package
agentgif badge url -p pypi -k colorfyi

# Markdown format only
agentgif badge url -p npm -k react --format md

# With a theme
agentgif badge url -p crates -k serde --theme dracula

# GitHub stars badge
agentgif badge url -p github -k "vercel/next.js" -m stars

# List available themes
agentgif badge themes
```

**Providers:** `pypi`, `npm`, `crates`, `github`
**Formats:** `url`, `md`, `html`, `img`, `all` (default)

## License

MIT
