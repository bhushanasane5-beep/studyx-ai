"""Minimal connectivity check for the NVIDIA NIM chat endpoint."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
PROMPT = "Explain Machine Learning in simple Hindi in 3 sentences."


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries without logging their values."""
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key and not key.lstrip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    if not ENV_PATH.exists():
        print("NVIDIA API connection failed: backend/.env was not found.")
        return 1

    load_env_file(ENV_PATH)
    api_key = os.environ.get("NVIDIA_API_KEY", "")
    model = os.environ.get("NVIDIA_MODEL", "")
    if not api_key or not model:
        print("NVIDIA API connection failed: NVIDIA_API_KEY or NVIDIA_MODEL is missing.")
        return 1

    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": PROMPT}],
            "temperature": 0.2,
            "max_tokens": 250,
        }
    ).encode("utf-8")
    request = Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data["choices"][0]["message"]["content"].strip()
    except HTTPError as error:
        print(f"NVIDIA API connection failed: server returned HTTP {error.code}.")
        return 1
    except (URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError):
        print("NVIDIA API connection failed.")
        return 1

    print("NVIDIA API connection succeeded.")
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
