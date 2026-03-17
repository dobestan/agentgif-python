# mypy: ignore-errors
"""Smoke tests for CLI commands."""

from unittest.mock import patch

from click.testing import CliRunner

from agentgif.cli import _detect_repo, main


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "AgentGIF" in result.output


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.2.0" in result.output


def test_whoami_not_logged_in() -> None:
    runner = CliRunner()
    with patch("agentgif.cli.get_api_key", return_value=None):
        result = runner.invoke(main, ["whoami"])
    assert result.exit_code == 1
    assert "Not logged in" in result.output


def test_search() -> None:
    runner = CliRunner()
    mock_results = {"count": 1, "results": [{"id": "abc", "title": "Test", "command": "ls"}]}
    with patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.search.return_value = mock_results
        result = runner.invoke(main, ["search", "test"])
    assert result.exit_code == 0
    assert "Test" in result.output


def test_detect_repo() -> None:
    """Repo detection from git remote."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "git@github.com:dobestan/colorfyi.git\n"
        assert _detect_repo() == "colorfyi"


def test_badge_url() -> None:
    runner = CliRunner()
    mock_data = {
        "url": "https://agentgif.com/badge/pypi/colorfyi/version.svg",
        "markdown": "[![colorfyi version](https://agentgif.com/badge/pypi/colorfyi/version.svg)](https://agentgif.com/badge/)",
        "html": '<a href="https://agentgif.com/badge/"><img src="https://agentgif.com/badge/pypi/colorfyi/version.svg" alt="colorfyi version"></a>',
        "img": '<img src="https://agentgif.com/badge/pypi/colorfyi/version.svg" alt="colorfyi version">',
    }
    with patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.badge_url.return_value = mock_data
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        result = runner.invoke(main, ["badge", "url", "-p", "pypi", "-k", "colorfyi"])
    assert result.exit_code == 0
    assert "version.svg" in result.output


def test_badge_url_format_md() -> None:
    runner = CliRunner()
    mock_data = {"url": "x", "markdown": "[![badge](url)](link)", "html": "h", "img": "i"}
    with patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.badge_url.return_value = mock_data
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        result = runner.invoke(main, ["badge", "url", "-p", "npm", "-k", "pkg", "--format", "md"])
    assert result.exit_code == 0
    assert "[![badge]" in result.output


def test_badge_themes() -> None:
    runner = CliRunner()
    mock_data = {
        "count": 2,
        "themes": [
            {"slug": "dracula", "name": "Dracula", "category": "dark", "preview_url": "https://example.com/preview"},
            {"slug": "nord", "name": "Nord", "category": "classic", "preview_url": "https://example.com/preview2"},
        ],
    }
    with patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.badge_themes.return_value = mock_data
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        result = runner.invoke(main, ["badge", "themes"])
    assert result.exit_code == 0
    assert "Dracula" in result.output
    assert "Nord" in result.output


def test_generate_github_url() -> None:
    runner = CliRunner()
    job_resp = {"job_id": "Ab3kM9xQ", "status": "pending", "status_url": "/api/v1/gifs/generate/Ab3kM9xQ/"}
    status_resp = {
        "job_id": "Ab3kM9xQ",
        "status": "completed",
        "commands_found": 3,
        "gifs_created": 2,
        "gifs": [
            {"id": "gif1", "title": "Demo 1", "url": "https://agentgif.com/gif1"},
            {"id": "gif2", "title": "Demo 2", "url": "https://agentgif.com/gif2"},
        ],
    }
    with patch("agentgif.cli.get_api_key", return_value="test-key"), patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        MockClient.return_value.generate_tape.return_value = job_resp
        MockClient.return_value.generate_status.return_value = status_resp
        result = runner.invoke(main, ["generate", "https://github.com/fyipedia/colorfyi"])
    assert result.exit_code == 0
    assert "2 GIFs generated" in result.output
    MockClient.return_value.generate_tape.assert_called_once_with(
        source_url="https://github.com/fyipedia/colorfyi",
        source_type="github",
        max_gifs=5,
        raw_markdown="",
    )


def test_generate_pypi() -> None:
    runner = CliRunner()
    job_resp = {"job_id": "Xy7zQ1wR", "status": "pending", "status_url": "/api/v1/gifs/generate/Xy7zQ1wR/"}
    status_resp = {"job_id": "Xy7zQ1wR", "status": "completed", "gifs_created": 1, "gifs": []}
    with patch("agentgif.cli.get_api_key", return_value="test-key"), patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        MockClient.return_value.generate_tape.return_value = job_resp
        MockClient.return_value.generate_status.return_value = status_resp
        result = runner.invoke(main, ["generate", "--pypi", "colorfyi"])
    assert result.exit_code == 0
    MockClient.return_value.generate_tape.assert_called_once_with(
        source_url="https://pypi.org/project/colorfyi/",
        source_type="pypi",
        max_gifs=5,
        raw_markdown="",
    )


def test_generate_npm() -> None:
    runner = CliRunner()
    job_resp = {"job_id": "Nm4pL8vS", "status": "pending", "status_url": "/api/v1/gifs/generate/Nm4pL8vS/"}
    status_resp = {"job_id": "Nm4pL8vS", "status": "completed", "gifs_created": 1, "gifs": []}
    with patch("agentgif.cli.get_api_key", return_value="test-key"), patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        MockClient.return_value.generate_tape.return_value = job_resp
        MockClient.return_value.generate_status.return_value = status_resp
        result = runner.invoke(main, ["generate", "--npm", "emojifyi"])
    assert result.exit_code == 0
    MockClient.return_value.generate_tape.assert_called_once_with(
        source_url="https://www.npmjs.com/package/emojifyi",
        source_type="npm",
        max_gifs=5,
        raw_markdown="",
    )


def test_generate_no_wait() -> None:
    runner = CliRunner()
    job_resp = {"job_id": "Ab3kM9xQ", "status": "pending", "status_url": "/api/v1/gifs/generate/Ab3kM9xQ/"}
    with patch("agentgif.cli.get_api_key", return_value="test-key"), patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        MockClient.return_value.generate_tape.return_value = job_resp
        result = runner.invoke(main, ["generate", "--no-wait", "https://github.com/fyipedia/colorfyi"])
    assert result.exit_code == 0
    assert "Ab3kM9xQ" in result.output
    assert "generate-status" in result.output
    MockClient.return_value.generate_status.assert_not_called()


def test_generate_not_logged_in() -> None:
    runner = CliRunner()
    with patch("agentgif.cli.get_api_key", return_value=None):
        result = runner.invoke(main, ["generate", "https://github.com/fyipedia/colorfyi"])
    assert result.exit_code == 1
    assert "Not logged in" in result.output


def test_generate_status_command() -> None:
    runner = CliRunner()
    status_resp = {
        "job_id": "Ab3kM9xQ",
        "status": "completed",
        "commands_found": 5,
        "gifs_created": 3,
        "gifs": [
            {"id": "g1", "title": "Install", "url": "https://agentgif.com/g1"},
        ],
    }
    with patch("agentgif.cli.get_api_key", return_value="test-key"), patch("agentgif.cli.Client") as MockClient:
        MockClient.return_value.cli_version.return_value = {"latest": "0.2.0"}
        MockClient.return_value.generate_status.return_value = status_resp
        result = runner.invoke(main, ["generate-status", "Ab3kM9xQ"])
    assert result.exit_code == 0
    assert "Ab3kM9xQ" in result.output
    assert "completed" in result.output
    assert "Install" in result.output
