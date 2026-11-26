"""Checks that importing modules does not start application interactions."""

import subprocess
import sys
import textwrap
from pathlib import Path


def test_imports_do_not_interact_with_terminal_or_http():
    script = textwrap.dedent(
        """
        import importlib
        from unittest.mock import patch

        import requests

        def forbidden(*args, **kwargs):
            raise AssertionError("Module import caused an unexpected side effect")

        with (
            patch("builtins.input", forbidden),
            patch("getpass.getpass", forbidden),
            patch("requests.sessions.Session.request", forbidden),
        ):
            for name in (
                "safeserve_tui",
                "safeserve_tui.domain",
                "safeserve_tui.menu",
                "safeserve_tui.api",
                "safeserve_tui.app",
                "safeserve_tui.__main__",
            ):
                importlib.import_module(name)
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        input="",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
