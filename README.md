# winfried-ripken.github.io

Personal academic website built with Jekyll and hosted on GitHub Pages.

## Main features

- Modern single-page homepage (`index.md`)
- Publication list rendered from `_data/publications.json`
- Automatic Google Scholar sync via GitHub Actions (`.github/workflows/update-publications.yml`)

## Publication sync

The sync script is `scripts/fetch_scholar.py`.

It reads your Scholar profile id from `_config.yml`:

```yml
scholar:
  user_id: "wAVKdLcAAAAJ"
```

Workflow behavior:

- Runs weekly (Monday, 03:17 UTC)
- Can also be triggered manually from GitHub Actions (`workflow_dispatch`)
- Updates `_data/publications.json` and commits changes automatically

## Local run

```bash
bundle install
bundle exec jekyll serve
```

Open `http://127.0.0.1:4000`.
