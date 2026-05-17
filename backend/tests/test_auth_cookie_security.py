import unittest
from pathlib import Path

from app.session_cookie_policy import should_secure_session_cookie


class AuthCookieSecurityTests(unittest.TestCase):
    def test_auto_cookie_policy_keeps_http_session_cookie_sendable(self) -> None:
        self.assertFalse(should_secure_session_cookie(None, "http"))

    def test_auto_cookie_policy_marks_https_session_cookie_secure(self) -> None:
        self.assertTrue(should_secure_session_cookie(None, "https"))

    def test_explicit_cookie_policy_overrides_request_scheme(self) -> None:
        self.assertTrue(should_secure_session_cookie(True, "http"))
        self.assertFalse(should_secure_session_cookie(False, "https"))

    def test_docker_compose_does_not_force_secure_cookie_by_default(self) -> None:
        compose_file = Path(__file__).resolve().parents[2] / "docker-compose.yml"

        compose_content = compose_file.read_text(encoding="utf-8")
        active_lines = self._active_lines(compose_content)

        self.assertFalse(any(line == "- SESSION_COOKIE_SECURE=true" for line in active_lines))
        self.assertFalse(any("SESSION_COOKIE_SECURE=${SESSION_COOKIE_SECURE:-true}" in line for line in active_lines))

    def test_container_entrypoint_accepts_trusted_proxy_headers(self) -> None:
        entrypoint_file = Path(__file__).resolve().parents[1] / "scripts" / "entrypoint.sh"

        entrypoint_content = entrypoint_file.read_text(encoding="utf-8")

        self.assertIn("--proxy-headers", entrypoint_content)
        self.assertIn("--forwarded-allow-ips", entrypoint_content)

    @staticmethod
    def _active_lines(content: str) -> list[str]:
        return [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]


if __name__ == "__main__":
    unittest.main()
