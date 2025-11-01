"""Update feed integration for the WordImperfect desktop client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
import json
import urllib.request

DEFAULT_FEED_URL = (
    "https://wordimperfect.github.io/WordImperfect/downloads/releases.json"
)
DEFAULT_DOWNLOAD_PAGE = "https://wordimperfect.github.io/WordImperfect/downloads/"


@dataclass(slots=True)
class DownloadArtifact:
    """Installer metadata surfaced to the end user."""

    name: str
    url: str
    sha256: str


@dataclass(slots=True)
class ReleaseMetadata:
    """Structured information about a published release."""

    version: str
    date: str
    notes: list[str]
    downloads: list[DownloadArtifact]
    deprecated: bool = False


@dataclass(slots=True)
class UpdateCheckResult:
    """Outcome of a release feed lookup."""

    is_update_available: bool
    current_version: str
    latest_release: ReleaseMetadata | None
    error: str | None = None


class UpdateService:
    """Coordinate release feed parsing and version comparisons."""

    def __init__(
        self,
        feed_url: str | None = None,
        download_page: str | None = None,
    ) -> None:
        self._feed_url = feed_url or DEFAULT_FEED_URL
        self._download_page = download_page or DEFAULT_DOWNLOAD_PAGE

    @property
    def feed_url(self) -> str:
        """Return the configured feed URL."""

        return self._feed_url

    @property
    def download_page(self) -> str:
        """Return the canonical download page for manual updates."""

        return self._download_page

    def check_for_updates(self, current_version: str) -> UpdateCheckResult:
        """Retrieve the latest release entry and compare versions."""

        try:
            feed = self._load_feed()
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return UpdateCheckResult(
                is_update_available=False,
                current_version=current_version,
                latest_release=None,
                error=str(exc),
            )

        latest = self._extract_latest_release(feed)
        if latest is None:
            return UpdateCheckResult(
                is_update_available=False,
                current_version=current_version,
                latest_release=None,
                error="No releases available in feed.",
            )

        is_newer = self._is_version_newer(latest.version, current_version)
        return UpdateCheckResult(
            is_update_available=is_newer,
            current_version=current_version,
            latest_release=latest,
            error=None,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_feed(self) -> dict[str, Any]:
        with urllib.request.urlopen(self._feed_url, timeout=5) as response:
            raw_data = response.read()
        data = json.loads(raw_data.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Release feed must be a JSON object.")
        if "releases" not in data:
            raise KeyError("Release feed missing 'releases' key.")
        return data

    def _extract_latest_release(self, feed: dict[str, Any]) -> ReleaseMetadata | None:
        releases = feed.get("releases")
        if not isinstance(releases, list) or not releases:
            return None

        parsed = [self._parse_release(entry) for entry in releases if entry]
        if not parsed:
            return None

        return max(parsed, key=lambda release: self._version_key(release.version))

    def _parse_release(self, entry: dict[str, Any]) -> ReleaseMetadata:
        version = str(entry.get("version", ""))
        date = str(entry.get("date", ""))
        notes = self._coerce_notes(entry.get("notes", []))
        downloads = self._coerce_downloads(entry.get("downloads", []))
        deprecated = bool(entry.get("deprecated", False))
        if not version:
            raise ValueError("Release entry missing version string.")
        return ReleaseMetadata(
            version=version,
            date=date,
            notes=notes,
            downloads=downloads,
            deprecated=deprecated,
        )

    def _coerce_notes(self, notes: Any) -> list[str]:
        if not isinstance(notes, Iterable) or isinstance(notes, (str, bytes)):
            return []
        coerced: list[str] = []
        for note in notes:
            if isinstance(note, str):
                coerced.append(note)
        return coerced

    def _coerce_downloads(self, downloads: Any) -> list[DownloadArtifact]:
        if not isinstance(downloads, Iterable):
            return []
        artifacts: list[DownloadArtifact] = []
        for entry in downloads:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", ""))
            url = str(entry.get("url", ""))
            sha256 = str(entry.get("sha256", ""))
            if not name or not url or not sha256:
                continue
            artifacts.append(DownloadArtifact(name=name, url=url, sha256=sha256))
        return artifacts

    def _is_version_newer(self, candidate: str, current: str) -> bool:
        return self._version_key(candidate) > self._version_key(current)

    def _version_key(self, version: str) -> tuple[int, ...]:
        components: list[int] = []
        for part in version.split("."):
            try:
                components.append(int(part))
            except ValueError:
                components.append(0)
        return tuple(components)


__all__ = [
    "DEFAULT_DOWNLOAD_PAGE",
    "DEFAULT_FEED_URL",
    "DownloadArtifact",
    "ReleaseMetadata",
    "UpdateCheckResult",
    "UpdateService",
]
