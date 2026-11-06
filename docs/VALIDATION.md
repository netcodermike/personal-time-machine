# Validation record

Authoring host: Windows, November 6, 2026. Requirements: Python 3.11+; Windows, macOS, Linux.

The README verification command is `python -m unittest -v`. The companion GitHub Actions workflow describes reproducible build/test checks. Merely including that workflow does not mean it ran successfully. Host-specific verification results are recorded before publication.

Manual acceptance steps are in README.md. GUI behavior, hardware sensors, permissions, audio output, and OS isolation need verification on their target platform; compilation alone cannot establish these properties.

## Authoring result

Passed: 2 Python unittest cases covering snapshot/deduplication, text diffs, restore bytes, existing-destination rejection, and revision traversal rejection. Temporary files were placed under the writable workspace because the execution sandbox restricts the default Windows temp directory. Timeline HTTP/visual check pending.

## Observed GitHub Actions result

Passed on November 6, 2026: [build/check run](https://github.com/netcodermike/personal-time-machine/actions/runs/42196058846).

Verified source commit: `8d64118da10107fb65afaa77c753825d9de4c8f3`.

Python unit tests for snapshots, deduplication, diffs, and safe restore.

This record may be committed after the linked source-validation run; the linked SHA identifies exactly what was checked. Native GUI/hardware acceptance remains manual as described in README.md.
