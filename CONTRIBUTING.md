# Contributing

Thanks for your interest in FrameScribe.

## Development setup

```bash
git clone https://github.com/AlexMatthers/framescribe
cd framescribe
uv sync --dev --no-workspace
uv run pytest
```

> `--no-workspace` matters if you have cloned this repo inside another uv workspace; it
> keeps FrameScribe standalone.

## Pull requests

- Keep changes focused; describe the *why*.
- Run `uv run ruff check .` and `uv run pytest` before opening a PR.
- New behaviour needs a test; new public API needs a docstring and a README/`docs` update.
- No secrets, no vendored third-party code, no personal filesystem paths.

## License

By contributing you agree your contributions are licensed under Apache-2.0.
