"""Device auth flow — client side."""

import time
import webbrowser

import httpx

from agentgif.config import get_base_url, set_credentials


def device_login() -> tuple[str, str]:
    """Run device auth flow. Returns (api_key, username).

    1. POST /api/v1/auth/device/ → get device_code + user_code
    2. Open browser to verification_url
    3. Poll /api/v1/auth/device/token/ until approved
    """
    base_url = get_base_url().rstrip("/")

    # 1. Initiate
    response = httpx.post(f"{base_url}/api/v1/auth/device/")
    response.raise_for_status()
    data = response.json()
    device_code: str = data["device_code"]
    verification_url: str = data["verification_url"]
    interval = data.get("interval", 5)
    expires_in = data.get("expires_in", 900)

    # 2. Open browser
    webbrowser.open(verification_url)

    # 3. Poll
    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        poll = httpx.post(
            f"{base_url}/api/v1/auth/device/token/",
            json={"device_code": device_code},
        )
        if poll.status_code == 200:
            result = poll.json()
            api_key = result["api_key"]
            username = result["username"]
            set_credentials(api_key, username)
            return api_key, username
        if poll.status_code == 410:
            raise TimeoutError("Device code expired. Run `agentgif login` again.")
        # 428 = pending, keep polling

    raise TimeoutError("Login timed out. Run `agentgif login` again.")
