import pytest

from wordimperfect.services.update_service import UpdateCheckResult, UpdateService


@pytest.fixture
def sample_feed() -> dict:
    return {
        "releases": [
            {
                "version": "0.1.1",
                "date": "2024-05-10",
                "notes": [
                    "Fixed a crash when exporting documents.",
                    "Improved table formatting fidelity.",
                ],
                "downloads": [
                    {
                        "name": "Windows",
                        "url": "https://example.test/win.exe",
                        "sha256": "deadbeef",
                    }
                ],
            },
            {
                "version": "0.1.0",
                "date": "2024-05-06",
                "notes": ["Initial release."],
                "downloads": [
                    {
                        "name": "Windows",
                        "url": "https://example.test/win-old.exe",
                        "sha256": "cafebabe",
                    }
                ],
            },
        ]
    }


def test_update_available(monkeypatch, sample_feed):
    service = UpdateService(feed_url="https://example.test/feed.json")
    monkeypatch.setattr(UpdateService, "_load_feed", lambda self: sample_feed)

    result = service.check_for_updates("0.1.0")

    assert isinstance(result, UpdateCheckResult)
    assert result.is_update_available is True
    assert result.error is None
    assert result.latest_release is not None
    assert result.latest_release.version == "0.1.1"
    assert result.latest_release.downloads[0].sha256 == "deadbeef"


def test_no_update_needed(monkeypatch, sample_feed):
    service = UpdateService(feed_url="https://example.test/feed.json")
    monkeypatch.setattr(UpdateService, "_load_feed", lambda self: sample_feed)

    result = service.check_for_updates("0.1.1")

    assert result.is_update_available is False
    assert result.latest_release is not None
    assert result.latest_release.version == "0.1.1"


def test_feed_error_returns_message(monkeypatch):
    service = UpdateService(feed_url="https://example.test/feed.json")

    def _boom(self):
        raise ValueError("broken feed")

    monkeypatch.setattr(UpdateService, "_load_feed", _boom)

    result = service.check_for_updates("0.1.0")

    assert result.is_update_available is False
    assert result.latest_release is None
    assert result.error == "broken feed"
