# winfried-ripken.github.io

Minimal academic website built with Jekyll and hosted on GitHub Pages.

## Repository structure

- `index.md`: homepage content
- `_layouts/default.html`: single layout
- `assets/css/site.css`: site styling
- `_data/publications.json`: cached publication data rendered on homepage
- `scripts/fetch_scholar.py`: Scholar fetch implementation
- `scripts/run_publications_sync.py`: shared local/CI sync entrypoint
- `.github/workflows/update-publications.yml`: weekly/manual publication sync

## Publication sync

The Scholar profile id is configured in `_config.yml`:

```yml
scholar:
  user_id: "wAVKdLcAAAAJ"
```

### Local test

```bash
python3 -m pip install -r scripts/requirements-publications.txt
python3 scripts/run_publications_sync.py --debug --attempts 3
```

If proxy setup causes issues:

```bash
python3 scripts/run_publications_sync.py --debug --attempts 3 --no-proxy
```

### GitHub Actions

- Workflow: `.github/workflows/update-publications.yml`
- Runs weekly and on manual trigger
- Commits changes to `_data/publications.json` automatically

## Local site preview

```bash
bundle install
bundle exec jekyll serve
```

Open `http://127.0.0.1:4000`.
