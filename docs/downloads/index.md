# Download WordImperfect

The WordImperfect release catalogue consolidates production installers, checksums, and change history. The page is designed to be published via GitHub Pages by enabling the `docs/` directory as the site root. Each release includes mirrored installers for major desktop platforms, the SHA-256 checksum required to validate downloads, and a synopsis lifted from the project changelog.

> **Tip for maintainers:** Update `docs/downloads/releases.json` as part of every release promotion. The in-app update checker consumes that feed, so edits published to GitHub Pages become visible to all clients immediately.

## Latest release

| Version | Date       | Platform | Download | SHA-256 |
|---------|------------|----------|----------|---------|
| 0.1.0   | 2024-05-06 | Windows (x64) | [WordImperfect-0.1.0-win-x64.exe](artifacts/WordImperfect-0.1.0-win-x64.exe) | `5df9f2def10ae784e9cc6f1212c9cdd649e1cf83755653253f55080b17dcb873` |
|         |            | macOS (Universal) | [WordImperfect-0.1.0-macos-universal.dmg](artifacts/WordImperfect-0.1.0-macos-universal.dmg) | `89b79ea04b2366b41be5c190fdc9abe0cf82eca9058b16dc02231e650801c48d` |
|         |            | Linux (x64) | [WordImperfect-0.1.0-linux-x64.AppImage](artifacts/WordImperfect-0.1.0-linux-x64.AppImage) | `6648c3d3cc217b9dcab533f3420a0d9f6d2c24ef84110d08213e9ac46bdbff84` |

### Release notes

The notes below are synchronized with [`CHANGELOG.md`](../../CHANGELOG.md) to make it easy for users to understand what changed between builds.

- Initialized the project structure with core directories and tooling.
- Added foundational documentation for engineers and contributors.
- Configured Python packaging metadata along with linting and testing toolchains.
- Introduced placeholder test scaffolding to validate the development workflow.

## Previous releases

Older installers remain available for teams that need to validate regressions or roll back in production. Retain at least the three most recent releases in this section and continue to surface their checksums.

| Version | Date | Platform | Download | SHA-256 |
|---------|------|----------|----------|---------|
| _None yet_ | – | – | – | – |

## Publishing checklist

1. Build installers for every supported platform using the packaging configuration in `packaging/`.
2. Upload the artifacts to the `docs/downloads/artifacts/` directory (or your chosen CDN) and recompute SHA-256 checksums with `sha256sum`.
3. Update `docs/downloads/releases.json` and the tables above with the new metadata and release notes.
4. Commit the changes, push to the `main` branch, and let GitHub Pages redeploy the static site.
5. Tag the repository using the semantic version string that matches the release feed entry.

## Rollback procedures

The rollback workflow is documented in detail in [`docs/release-support.md`](../release-support.md). A condensed summary:

- Keep at least the last three installers per platform in the `artifacts/` directory.
- Validate the checksum of any installer you reissue to end users before distribution.
- Update the release feed with a `"deprecated": true` flag when you need to steer clients away from a problematic build.
- Communicate the rollback plan in the changelog so engineers understand remediation steps.

