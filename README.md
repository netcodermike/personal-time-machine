# Personal Time Machine

Keep immutable snapshots of a folder, compare text changes, restore a revision to a new directory, and browse a local visual timeline.

**Language:** Python 3.11+  
**Platform:** Windows, macOS, Linux  
**Status:** First-release learning project. See implemented scope and limitations below; this is not a production-completeness claim.

## Features

- SHA-256 content-addressed object storage deduplicates identical file contents.
- Named snapshots preserve relative file paths and creation timestamps.
- Unified UTF-8 text diffs and binary change notices.
- Restores verify object hashes and refuse existing destination folders.
- Read-only HTML timeline at http://127.0.0.1:8080.

## Requirements and quick start

Clone the repository, enter its folder, and install the language/platform tools listed above. Commands run from the repository root. No credentials are required except for Backup Vault's explicitly generated secrets.

```sh
git clone https://github.com/netcodermike/personal-time-machine.git
cd personal-time-machine
python timemachine.py /path/to/folder snapshot --label "Before refactor"
python timemachine.py /path/to/folder list
python timemachine.py /path/to/folder diff OLDER_ID NEWER_ID
python timemachine.py /path/to/folder restore REVISION_ID /path/to/new-folder
python timemachine.py /path/to/folder serve --port 8080
```

## Verification

```sh
python -m unittest -v
```

Create `sample/hello.txt`, snapshot it, edit it, and snapshot again. `diff` should show the edit. Restore the first ID to a new folder and compare bytes. Take an identical snapshot and confirm the object count does not grow. Start `serve` and inspect both labels in the timeline.

See [validation notes](docs/VALIDATION.md) for what was actually executed during authoring. A committed CI workflow is a future check until its run is observed successful.

## Architecture and data

`timemachine.py` owns the CLI, `History` storage API, atomic writes, and the timeline HTTP handler. `test_timemachine.py` checks deduplication, diffs, restore behavior, and revision validation.

The source folder contains `.time-machine/objects/<sha256>` and `.time-machine/snapshots/<revision>.json`. Snapshot manifests map relative paths to content hashes. Temporary files are created beside their destination and replaced atomically. Snapshot creation is synchronous; stop writers for a consistent multi-file snapshot.

## Limitations and next steps

File contents only: permissions, empty folders, hard links, symlinks, and timestamps are not preserved. `.git` and `.time-machine` directories are excluded. Large files are read into memory. Snapshots are not encrypted. There is no pruning, watcher, search, or scheduled backup yet. The timeline lists snapshots; use the CLI for diffs and restores. A snapshot on the same disk is not protection from disk failure.

## Troubleshooting

An existing restore destination is intentionally rejected; choose a new directory. A missing object means the store is incomplete. A hash mismatch means corruption: recover the object from another backup. If port 8080 is occupied, pass a different `--port`. On Windows quote paths containing spaces. Stop the timeline with Ctrl+C.

## Development

Read the source entry point described above, make a focused change, run the verification command, and exercise the relevant manual scenario. [Contributing](CONTRIBUTING.md) explains bug reports and pull requests; [security notes](SECURITY.md) describe the trust assumptions. Runtime/generated files are ignored. No telemetry or paid API dependencies are included.

## License

[MIT](LICENSE), copyright 2026 netcodermike.
