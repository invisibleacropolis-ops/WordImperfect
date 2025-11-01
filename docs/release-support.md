# Release support and rollback procedures

This guide outlines how to maintain historical WordImperfect installers, publish fixes safely, and roll back if an issue escapes into production. The checklist is optimized for teams hosting the GitHub Pages site at `docs/downloads/`.

## Artifact retention policy

- Retain at least the most recent three releases for every supported platform inside `docs/downloads/artifacts/`.
- Include the SHA-256 checksum for every artifact in `docs/downloads/releases.json`. Never distribute an installer whose checksum is missing or unverified.
- When superseding an installer, keep the previous artifact online for a minimum of 30 days to support customer escalations.

## Rollback decision tree

1. **Identify severity.** If the regression blocks editing or data export, initiate rollback. For cosmetic issues, issue a hotfix instead.
2. **Select fallback build.** Choose the newest release with acceptable quality. Confirm its checksum matches the recorded value.
3. **Update the release feed.**
   - Move the fallback release to the top of `releases` in `docs/downloads/releases.json`.
   - Add `{ "deprecated": true }` to the problematic release so clients can display a warning.
   - Publish an advisory in `CHANGELOG.md` describing the incident and remediation steps.
4. **Communicate to users.** Send an announcement linking to the fallback installer and share manual rollback instructions if required.

## Manual rollback steps for end users

1. Download the fallback installer from the [Download WordImperfect](downloads/index.md) page.
2. Validate the checksum using `sha256sum <file>` on Linux/macOS or `CertUtil -hashfile <file> SHA256` on Windows.
3. Uninstall the currently deployed version of WordImperfect.
4. Run the fallback installer and launch the application.
5. Disable automatic updates temporarily if repeated rollbacks are expected.

## Maintaining the release feed

The application consumes `docs/downloads/releases.json` to determine whether an update is available.

- Keep the `releases` array sorted from newest to oldest.
- Populate the optional `deprecated` flag when you need to steer clients away from a release.
- Include concise release notes in the `notes` array. Reuse the content already curated in `CHANGELOG.md`.
- Whenever you add a new entry, bump the version constant in `src/wordimperfect/__init__.py` as part of the release branch.

## Automation hooks

- Integrate the checksum calculation into your CI pipeline. Emit the updated JSON snippet as a build artifact.
- As part of the release job, deploy the refreshed `docs/` directory so GitHub Pages stays synchronized.
- Schedule a nightly job that validates the availability of every download URL and sends alerts if a link breaks.

Maintaining a tight feedback loop between the packaged installers, the release feed, and the in-app update checker ensures WordImperfect users can trust every published build.

