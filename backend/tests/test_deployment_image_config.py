import unittest
from pathlib import Path


GHCR_IMAGE = "ghcr.io/shenyanshu/mumuainovel:latest"
LEGACY_DOCKER_HUB_IMAGE = "mumujie/mumuainovel:latest"


class DeploymentImageConfigTests(unittest.TestCase):
    def test_compose_uses_forked_ghcr_image(self) -> None:
        compose_content = self._repo_file("docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn(f"image: {GHCR_IMAGE}", compose_content)
        self.assertNotIn(f"image: {LEGACY_DOCKER_HUB_IMAGE}", compose_content)

    def test_readme_uses_forked_ghcr_image(self) -> None:
        readme_content = self._repo_file("README.md").read_text(encoding="utf-8")

        self.assertIn(GHCR_IMAGE, readme_content)
        self.assertNotIn(LEGACY_DOCKER_HUB_IMAGE, readme_content)

    @staticmethod
    def _repo_file(relative_path: str) -> Path:
        return Path(__file__).resolve().parents[2] / relative_path


if __name__ == "__main__":
    unittest.main()
