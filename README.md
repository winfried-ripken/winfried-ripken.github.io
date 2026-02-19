# winfried-ripken.github.io

Personal academic website built with Jekyll and hosted on GitHub Pages.

## Main features

- Modern single-page homepage (`index.md`)
- Publication list rendered from `_data/publications.json`
- Automatic Google Scholar sync via GitHub Actions (`.github/workflows/update-publications.yml`)

## Publication sync

The shared sync entrypoint (used by both local runs and GitHub Actions) is:

- `scripts/run_publications_sync.py`

Internally it calls `scripts/fetch_scholar.py` so both paths use the exact same fetch logic.

It reads your Scholar profile id from `_config.yml`:

```yml
scholar:
  user_id: "wAVKdLcAAAAJ"
```

Workflow behavior:

- Runs weekly (Monday, 03:17 UTC)
- Can also be triggered manually from GitHub Actions (`workflow_dispatch`)
- Updates `_data/publications.json` and commits changes automatically

### Test publication sync locally

```bash
python3 -m pip install -r scripts/requirements-publications.txt
python3 scripts/run_publications_sync.py --debug --attempts 3
```

If proxy setup is problematic on your machine, run:

```bash
python3 scripts/run_publications_sync.py --debug --attempts 3 --no-proxy
```

## Local run

```bash
bundle install
bundle exec jekyll serve
```

Open `http://127.0.0.1:4000`.
