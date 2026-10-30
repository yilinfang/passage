# passage

This repository is a personal fork of [passage](https://github.com/FiloSottile/passage) by Filippo Valsorda.
I modify it to fit my own use. You are welcome to use it too, but changes are driven by my own needs and there are no compatibility promises beyond what is written here.
Only macOS is tested.

See original [README](README).

## Recommended installation method (macOS)

Make sure that `~/.local/bin` is in your `$PATH`, and that `~/.local/share/zsh/site-functions` is in your `fpath` before `compinit` runs (with oh-my-zsh, before it is sourced):

```zsh
# in ~/.zshrc
fpath=(~/.local/share/zsh/site-functions $fpath)
```

Then install:

```bash
PREFIX="$HOME/.local" WITH_ZSHCOMP=yes make install
rm -f "${ZDOTDIR:-$HOME}"/.zcompdump*   # clear the completion cache
```

To uninstall, use the same prefix:

```bash
PREFIX="$HOME/.local" make uninstall
```

## Changes in this fork

- `passage grep` skips YubiKey-protected directories when no YubiKey is connected, so it does not prompt once per secret. See [YubiKey directories](#yubikey-directories).
- The macOS ramdisk used by `passage edit` is attached with `diskutil image attach`, because `hdiutil attach -nomount` is deprecated and prints a warning on recent macOS. It falls back to `hdid` on older systems.

## YubiKey directories

Following the rule of ["Convention over Configuration"](https://en.wikipedia.org/wiki/Convention_over_configuration), this fork treats top-level directories named `yubikey` or `yubikey-*` as **YubiKey-protected**. For convenience, `passage grep` skips them when no YubiKey is connected.

You should create a **separate** `.age-recipients` file with your YubiKey recipients inside each of these directories.

You should **not put normal secrets** here, otherwise `passage grep` skips them when no YubiKey is connected.

## License

GPLv2 or later, the same as password-store. See [COPYING](COPYING).
