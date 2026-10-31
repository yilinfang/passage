# passage

This repository is a personal fork of [passage](https://github.com/FiloSottile/passage) by Filippo Valsorda.
I modify it to fit my own use. You are welcome to use it too, but changes are driven by my own needs and there are no compatibility promises beyond what is written here.

Only macOS is tested.

See original [README](README).

## Dependencies (macOS)

- `age` or `rage`
- `gnu-getopt`
- `tree`
- `qrencode`
- `age-plugin-yubikey` (optional)

## Recommended installation method (macOS)

Make sure that `~/.local/bin` is in your `$PATH`.

### Zsh completion (optional)

Make sure that `~/.local/share/zsh/site-functions` is in your `fpath` before `compinit` runs (with oh-my-zsh, before it is sourced):

```zsh
# in ~/.zshrc
fpath=(~/.local/share/zsh/site-functions $fpath)
```

### Install

This also installs the completion file. It has no effect if you skip the step above.

```bash
PREFIX="$HOME/.local" WITH_ZSHCOMP=yes make install
rm -f "${ZDOTDIR:-$HOME}"/.zcompdump*   # clear the completion cache (only needed for zsh completion)
```

To uninstall, use the same prefix:

```bash
PREFIX="$HOME/.local" make uninstall
```

## Changes in this fork

- `passage grep` skips YubiKey-protected directories, so that one command cannot decrypt all of your critical secrets. See [YubiKey directories](#yubikey-directories).
- The macOS ramdisk for `passage edit` is attached with `diskutil image attach`. Upstream uses `hdid`, which is deprecated and prints a warning on recent macOS. If `diskutil image attach` is not available, it falls back to `hdid`.

## YubiKey directories

Following the rule of ["Convention over Configuration"](https://en.wikipedia.org/wiki/Convention_over_configuration), this fork treats top-level directories named `yubikey` or `yubikey-*` as **YubiKey-protected**. `passage grep` skips them, because it decrypts every secret it searches, and with a cached or disabled touch policy one touch would expose all of them. To search them anyway, set `PASSAGE_DANGEROUS_GREP_YUBIKEY=1`.

You should create a **separate** `.age-recipients` file with your YubiKey recipients inside each of these directories.

You should **not put normal secrets** here, otherwise `passage grep` skips them.

## License

GPLv2 or later, the same as password-store. See [COPYING](COPYING).
