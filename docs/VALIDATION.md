# Validation record

Authoring host: Windows, November 6, 2026. Requirements: Python 3.11+; Windows, macOS, Linux.

The README verification command is `python -m unittest -v`. The companion GitHub Actions workflow describes reproducible build/test checks. Merely including that workflow does not mean it ran successfully. Host-specific verification results are recorded before publication.

Manual acceptance steps are in README.md. GUI behavior, hardware sensors, permissions, audio output, and OS isolation need verification on their target platform; compilation alone cannot establish these properties.

## Authoring result

Passed: 2 Python unittest cases covering snapshot/deduplication, text diffs, restore bytes, existing-destination rejection, and revision traversal rejection. Temporary files were placed under the writable workspace because the execution sandbox restricts the default Windows temp directory. Timeline HTTP/visual check pending.
