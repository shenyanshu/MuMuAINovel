import importlib
import sys
import types
import unittest
from types import SimpleNamespace


class StubHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _load_security_module():
    if "fastapi" not in sys.modules:
        fastapi_stub = types.ModuleType("fastapi")
        setattr(fastapi_stub, "HTTPException", StubHTTPException)
        sys.modules["fastapi"] = fastapi_stub

    if "app.config" not in sys.modules:
        config_stub = types.ModuleType("app.config")
        setattr(config_stub, "settings", SimpleNamespace())
        sys.modules["app.config"] = config_stub

    return importlib.import_module("app.security")


security = _load_security_module()


class HttpUrlValidationTests(unittest.TestCase):
    def test_optional_http_url_allows_empty_base_url(self) -> None:
        self.assertEqual(security.validate_optional_http_url(None), "")
        self.assertEqual(security.validate_optional_http_url(""), "")

    def test_optional_http_url_reuses_required_url_validation(self) -> None:
        self.assertEqual(
            security.validate_optional_http_url("http://127.0.0.1:11434/v1/"),
            "http://127.0.0.1:11434/v1",
        )

    def test_allows_self_hosted_local_and_private_http_urls(self) -> None:
        allowed_urls = [
            "http://localhost:11434/v1",
            "http://127.0.0.1:11434/v1",
            "http://192.168.31.10:8000/v1",
            "http://10.0.0.5:8000/v1",
            "http://host.docker.internal:11434/v1",
        ]

        for raw_url in allowed_urls:
            with self.subTest(raw_url=raw_url):
                self.assertEqual(security.validate_http_url(raw_url), raw_url)

    def test_rejects_non_http_url(self) -> None:
        with self.assertRaises(security.HTTPException) as caught:
            security.validate_http_url("file:///etc/passwd")

        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.detail, "仅支持 HTTP/HTTPS URL")

    def test_rejects_url_without_hostname(self) -> None:
        with self.assertRaises(security.HTTPException) as caught:
            security.validate_http_url("http:///v1")

        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.detail, "URL缺少主机名")

    def test_rejects_url_with_invalid_port(self) -> None:
        with self.assertRaises(security.HTTPException) as caught:
            security.validate_http_url("http://localhost:invalid/v1")

        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.detail, "URL端口无效")

    def test_rejects_url_with_embedded_credentials(self) -> None:
        with self.assertRaises(security.HTTPException) as caught:
            security.validate_http_url("https://user:pass@example.com/v1")

        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.detail, "URL不允许包含认证信息")


if __name__ == "__main__":
    unittest.main()
