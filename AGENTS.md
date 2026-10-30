# AGENTS.md

passage is a personal fork of [FiloSottile/passage](https://github.com/FiloSottile/passage), which is password-store (`pass`) with age instead of GnuPG. Only macOS is tested. `README` is the upstream README; `README.md` documents this fork.

## Running and testing

There is no build, linter, or test suite. To try a change without touching the real store, run the script from the repo (it finds `src/platform/` relative to itself) against a throwaway store:

```bash
T="$(mktemp -d)"; age-keygen -o "$T/id" 2>/dev/null
PASSAGE_DIR="$T/store" PASSAGE_IDENTITIES_FILE="$T/id" bash src/password-store.sh generate foo/bar
PASSAGE_DIR="$T/store" PASSAGE_IDENTITIES_FILE="$T/id" bash src/password-store.sh show foo/bar
```

The script exits early if the identities file does not exist. Install for real with `PREFIX="$HOME/.local" WITH_ZSHCOMP=yes make install`.

## Conventions

- Match the upstream style: tab indentation, `local` variables, `die` for errors, `$GETOPT` option parsing with `eval set --`.
- Commit subjects use a component prefix: `passage:`, `platform/darwin:`, `README:`.
- When a change alters behaviour from upstream, add it to "Changes in this fork" in `README.md`.
- New subcommands also need entries in `cmd_usage` and the completion files in `src/completion/`.
