# mypy: ignore-errors
"""AgentGIF CLI — upload, manage, and share terminal GIFs."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from importlib.metadata import version as pkg_version
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from agentgif.auth import device_login
from agentgif.client import AgentGIFError, Client
from agentgif.config import clear_credentials, get_api_key

console = Console()

_VERSION = pkg_version("agentgif")


def _check_for_updates() -> None:
    """Best-effort version check — never blocks or crashes."""
    try:
        data = Client().cli_version()
        latest = data.get("latest", "")
        if latest and latest != _VERSION:
            console.print(f"[yellow]Update available: {_VERSION} → {latest}. Run: pip install -U agentgif[/yellow]")
    except Exception:  # noqa: BLE001
        pass  # Network errors, API errors — silently ignore


def _detect_repo() -> str:
    """Detect repo slug from git remote origin."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # git@github.com:user/repo.git → repo
            # https://github.com/user/repo.git → repo
            name = url.rstrip("/").rsplit("/", 1)[-1]
            return name.removesuffix(".git")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


@click.group()
@click.version_option(version=_VERSION)
def main() -> None:
    """AgentGIF — GIF for humans. Cast for agents."""
    _check_for_updates()


@main.command()
def login() -> None:
    """Authenticate with AgentGIF via browser."""
    console.print("[bold]Opening browser for authentication...[/bold]")
    try:
        api_key, username = device_login()
        console.print(f"[green]✓ Logged in as @{username}[/green]")
    except TimeoutError as e:
        console.print(f"[red]✗ {e}[/red]")
        sys.exit(1)


@main.command()
def logout() -> None:
    """Remove stored credentials."""
    clear_credentials()
    console.print("[green]✓ Logged out[/green]")


@main.command()
def whoami() -> None:
    """Show current user info."""
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)
    try:
        client = Client()
        user = client.whoami()
        console.print(f"@{user['username']} — {user.get('display_name', '')}")
        console.print(f"GIFs: {user.get('upload_count', 0)}")
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)


@main.command()
@click.argument("gif_path", type=click.Path(exists=True, path_type=Path))
@click.option("--title", "-t", default="", help="GIF title")
@click.option("--description", "-d", default="", help="Description")
@click.option("--command", "-c", default="", help="Command demonstrated")
@click.option("--tags", default="", help="Comma-separated tags")
@click.option("--cast", "cast_path", type=click.Path(exists=True, path_type=Path), default=None, help="Cast file")
@click.option("--theme", default="", help="Terminal theme slug")
@click.option("--unlisted", is_flag=True, help="Upload as unlisted")
@click.option("--no-repo", is_flag=True, help="Don't auto-detect repo")
def upload(
    gif_path: Path,
    title: str,
    description: str,
    command: str,
    tags: str,
    cast_path: Path | None,
    theme: str,
    unlisted: bool,
    no_repo: bool,
) -> None:
    """Upload a GIF to AgentGIF."""
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)

    repo_slug = "" if no_repo else _detect_repo()
    visibility = "unlisted" if unlisted else "public"

    with console.status("Uploading..."):
        try:
            client = Client()
            result = client.upload(
                gif_path,
                title=title,
                description=description,
                command=command,
                tags=tags,
                cast_path=cast_path,
                theme=theme,
                visibility=visibility,
                repo_slug=repo_slug,
            )
        except AgentGIFError as e:
            console.print(f"[red]Upload failed: {e.message}[/red]")
            sys.exit(1)

    console.print(f"[green]✓ Uploaded:[/green] {result['url']}")
    console.print(f"  Embed: {result['embed']['markdown']}")


@main.command()
@click.argument("query")
def search(query: str) -> None:
    """Search public GIFs."""
    client = Client()
    results = client.search(query)
    table = Table(title=f"Search: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Command", style="green")
    for gif in results.get("results", []):
        table.add_row(gif["id"], gif["title"], gif.get("command", ""))
    console.print(table)


@main.command("list")
@click.option("--repo", default="", help="Filter by repo slug")
def list_gifs(repo: str) -> None:
    """List your GIFs."""
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)
    client = Client()
    params = {}
    if repo:
        params["repo"] = repo
    results = client.list_gifs(**params)
    table = Table(title="My GIFs")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Views", justify="right")
    for gif in results.get("results", []):
        table.add_row(gif["id"], gif["title"], str(gif.get("view_count", 0)))
    console.print(table)


@main.command()
@click.argument("gif_id")
def info(gif_id: str) -> None:
    """Show GIF details (JSON)."""
    client = Client()
    data = client.get_gif(gif_id)
    console.print_json(json.dumps(data, indent=2))


@main.command()
@click.argument("gif_id")
@click.option("--format", "fmt", type=click.Choice(["md", "html", "iframe", "script", "all"]), default="all")
def embed(gif_id: str, fmt: str) -> None:
    """Show embed codes for a GIF."""
    client = Client()
    codes = client.embed_codes(gif_id)
    if fmt == "all":
        for name, code in codes.items():
            console.print(f"[bold]{name}:[/bold]")
            console.print(code)
            console.print()
    else:
        key_map = {"md": "markdown", "html": "html", "iframe": "iframe", "script": "script"}
        console.print(codes.get(key_map.get(fmt, fmt), ""))


@main.command()
@click.argument("gif_id")
@click.confirmation_option(prompt="Are you sure you want to delete this GIF?")
def delete(gif_id: str) -> None:
    """Delete a GIF."""
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)
    client = Client()
    try:
        client.delete_gif(gif_id)
        console.print(f"[green]✓ Deleted {gif_id}[/green]")
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)


@main.command()
@click.argument("gif_id")
@click.option("--title", "-t", default=None, help="New title")
@click.option("--description", "-d", default=None, help="New description")
@click.option("--command", "-c", default=None, help="New command")
@click.option("--tags", default=None, help="New comma-separated tags")
def update(gif_id: str, title: str | None, description: str | None, command: str | None, tags: str | None) -> None:
    """Update a GIF's metadata."""
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)
    fields = {}
    if title is not None:
        fields["title"] = title
    if description is not None:
        fields["description"] = description
    if command is not None:
        fields["command"] = command
    if tags is not None:
        fields["tags"] = tags
    if not fields:
        console.print("[yellow]No fields to update. Use --title, --description, --command, or --tags.[/yellow]")
        sys.exit(1)
    client = Client()
    try:
        result = client.update_gif(gif_id, **fields)
        console.print(f"[green]✓ Updated {gif_id}:[/green] {result['title']}")
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)


@main.command()
@click.argument("source", required=False, default="")
@click.option("--pypi", "pypi_pkg", default="", help="PyPI package name")
@click.option("--npm", "npm_pkg", default="", help="npm package name")
@click.option("--max", "max_gifs", default=5, type=int, help="Maximum GIFs to generate")
@click.option("--no-wait", is_flag=True, help="Return job ID immediately without polling")
@click.option("--stdin", "use_stdin", is_flag=True, help="Read markdown from stdin")
@click.option("--tape-only", is_flag=True, help="Generate tape scripts without recording GIFs")
@click.option("--theme", default="", help="Terminal theme for recording (e.g., dracula, monokai)")
def generate(
    source: str, pypi_pkg: str, npm_pkg: str, max_gifs: int, no_wait: bool, use_stdin: bool, tape_only: bool, theme: str
) -> None:
    """Generate demo GIFs from a README or package docs.

    \b
    Examples:
      agentgif generate https://github.com/fyipedia/colorfyi
      agentgif generate --pypi colorfyi
      agentgif generate --npm emojifyi
      agentgif generate --max 3 https://github.com/fyipedia/colorfyi
      agentgif generate --no-wait https://github.com/fyipedia/colorfyi
      cat README.md | agentgif generate --stdin
    """
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)

    source_url = source
    source_type = ""
    raw_markdown = ""

    if pypi_pkg:
        source_url = f"https://pypi.org/project/{pypi_pkg}/"
        source_type = "pypi"
    elif npm_pkg:
        source_url = f"https://www.npmjs.com/package/{npm_pkg}"
        source_type = "npm"
    elif use_stdin:
        if sys.stdin.isatty():
            console.print("[red]No input on stdin. Pipe markdown: cat README.md | agentgif generate --stdin[/red]")
            sys.exit(1)
        raw_markdown = sys.stdin.read()
    elif source and "github.com" in source:
        source_type = "github"

    if not source_url and not raw_markdown:
        console.print("[red]Provide a source URL, --pypi, --npm, or --stdin.[/red]")
        sys.exit(1)

    client = Client()
    try:
        job = client.generate_tape(
            source_url=source_url,
            source_type=source_type,
            max_gifs=max_gifs,
            raw_markdown=raw_markdown,
            tape_only=tape_only,
            theme=theme,
        )
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)

    job_id = job["job_id"]

    if no_wait:
        console.print(f"[green]Job created:[/green] {job_id}")
        console.print(f"  Status URL: {job.get('status_url', '')}")
        console.print(f"  Check: agentgif generate-status {job_id}")
        return

    with console.status("[bold]Generating GIFs...") as status:
        start = time.monotonic()
        prev_status = ""
        while time.monotonic() - start < 300:
            try:
                data = client.generate_status(job_id)
            except AgentGIFError as e:
                if e.status_code < 500:
                    console.print(f"[red]Error: {e.message}[/red]")
                    sys.exit(1)
                time.sleep(2)
                continue

            current = data.get("status", "")
            if current != prev_status:
                status.update(f"[bold]{current.capitalize()}...")
                prev_status = current

            if current == "completed":
                break
            if current == "failed":
                console.print(f"[red]Generation failed: {data.get('error_message', 'Unknown error')}[/red]")
                sys.exit(1)

            time.sleep(2)
        else:
            console.print("[red]Timed out after 5 minutes. Check status:[/red]")
            console.print(f"  agentgif generate-status {job_id}")
            sys.exit(1)

    tape_scripts = data.get("tape_scripts", [])
    gifs = data.get("gifs", [])

    if tape_only and tape_scripts:
        console.print(f"[green]Done! {len(tape_scripts)} tape scripts generated.[/green]")
        for script in tape_scripts:
            console.print(f"\n[bold cyan]── {script.get('title', script.get('slug', ''))} ──[/bold cyan]")
            console.print(script.get("content", ""))
    else:
        console.print(f"[green]Done! {data.get('gifs_created', len(gifs))} GIFs generated.[/green]")
        if gifs:
            table = Table(title="Generated GIFs")
            table.add_column("ID", style="cyan")
            table.add_column("Title")
            table.add_column("URL")
            for gif in gifs:
                table.add_row(gif.get("id", ""), gif.get("title", ""), gif.get("url", ""))
            console.print(table)


@main.command("generate-status")
@click.argument("job_id")
def generate_status(job_id: str) -> None:
    """Check status of a generate job."""
    if not get_api_key():
        console.print("[red]Not logged in. Run: agentgif login[/red]")
        sys.exit(1)
    client = Client()
    try:
        data = client.generate_status(job_id)
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)

    status = data.get("status", "unknown")
    console.print(f"[bold]Job:[/bold] {job_id}")
    console.print(f"[bold]Status:[/bold] {status}")

    if data.get("commands_found"):
        console.print(f"[bold]Commands found:[/bold] {data['commands_found']}")
    if data.get("gifs_created"):
        console.print(f"[bold]GIFs created:[/bold] {data['gifs_created']}")
    if data.get("error_message"):
        console.print(f"[red]Error: {data['error_message']}[/red]")

    gifs = data.get("gifs", [])
    if gifs:
        table = Table(title="Generated GIFs")
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("URL")
        for gif in gifs:
            table.add_row(gif.get("id", ""), gif.get("title", ""), gif.get("url", ""))
        console.print(table)


# -- Badge commands --


@main.group()
def badge() -> None:
    """Terminal-themed package badges (shields.io alternative)."""


@badge.command("url")
@click.option(
    "--provider", "-p", required=True, type=click.Choice(["pypi", "npm", "crates", "github"]), help="Package registry"
)
@click.option("--package", "-k", required=True, help="Package name (e.g. colorfyi, @scope/pkg, owner/repo)")
@click.option("--metric", "-m", default="version", help="Badge metric (version, downloads, stars, etc.)")
@click.option("--theme", default="", help="Terminal theme slug (e.g. dracula)")
@click.option("--style", default="", help="Badge style (default, flat)")
@click.option(
    "--format", "fmt", type=click.Choice(["url", "md", "html", "img", "all"]), default="all", help="Output format"
)
def badge_url(provider: str, package: str, metric: str, theme: str, style: str, fmt: str) -> None:
    """Generate a badge URL and embed codes."""
    client = Client()
    try:
        data = client.badge_url(provider, package, metric=metric, theme=theme, style=style)
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)

    if fmt == "all":
        console.print(f"[bold]URL:[/bold]  {data['url']}")
        console.print("[bold]Markdown:[/bold]")
        console.print(data["markdown"], markup=False)
        console.print("[bold]HTML:[/bold]")
        console.print(data["html"], markup=False)
        console.print("[bold]Image:[/bold]")
        console.print(data["img"], markup=False)
    elif fmt == "url":
        console.print(data["url"], markup=False)
    elif fmt == "md":
        console.print(data["markdown"], markup=False)
    elif fmt == "html":
        console.print(data["html"], markup=False)
    elif fmt == "img":
        console.print(data["img"], markup=False)


@badge.command("themes")
def badge_themes() -> None:
    """List available terminal themes for badges."""
    client = Client()
    try:
        data = client.badge_themes()
    except AgentGIFError as e:
        console.print(f"[red]Error: {e.message}[/red]")
        sys.exit(1)

    table = Table(title=f"Badge Themes ({data['count']})")
    table.add_column("Slug", style="cyan")
    table.add_column("Name")
    table.add_column("Category", style="green")
    table.add_column("Preview URL", style="dim")
    for t in data["themes"]:
        table.add_row(t["slug"], t["name"], t["category"], t["preview_url"])
    console.print(table)


@main.command()
@click.argument("tape_path", type=click.Path(exists=True, path_type=Path))
@click.option("--theme", default="", help="Terminal theme for recording")
@click.pass_context
def record(ctx: click.Context, tape_path: Path, theme: str) -> None:
    """Record a VHS tape → generate GIF + cast → upload.

    Requires VHS (https://github.com/charmbracelet/vhs) installed.
    """
    # 1. Run VHS to generate GIF
    output_gif = tape_path.with_suffix(".gif")
    console.print(f"[bold]Running VHS: {tape_path}[/bold]")
    result = subprocess.run(
        ["vhs", str(tape_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console.print(f"[red]VHS failed:[/red]\n{result.stderr}")
        sys.exit(1)

    if not output_gif.exists():
        console.print(f"[red]Expected output not found: {output_gif}[/red]")
        sys.exit(1)

    # 2. Look for a cast file (VHS generates it if tape has `Set CastFile`)
    cast_file = tape_path.with_suffix(".cast")
    cast_path = cast_file if cast_file.exists() else None

    # 3. Upload
    console.print("[bold]Uploading...[/bold]")
    ctx.invoke(
        upload,
        gif_path=output_gif,
        title=tape_path.stem.replace("-", " ").replace("_", " ").title(),
        cast_path=cast_path,
        theme=theme,
        command="",
        description="",
        tags="",
        unlisted=False,
        no_repo=False,
    )
