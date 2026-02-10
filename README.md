# Sample Hugo Website

## Run locally

1) Install Hugo (extended not required for this sample).
2) From this folder:

```bash
hugo server
```

Then open the URL Hugo prints (usually `http://localhost:1313`).

## Supporters email form

The home page includes a simple signup form (name + email). Because Hugo is static, you must point the form to a hosted form handler.

### Switch form providers

Set `params.supporters_form_provider` in `config.toml`:

- `generic` (default): POSTs to any endpoint you provide
- `formspree`: same as generic, but intended for Formspree
- `netlify`: uses Netlify Forms (no action URL required)

### Generic / Formspree

1) Create a form endpoint with a provider (example: Formspree).
2) Set the provider + endpoint in `config.toml`:

```toml
[params]
supporters_form_provider = "formspree"
supporters_form_action = "https://formspree.io/f/yourFormId"
```

If `supporters_form_action` is empty, the form renders but the submit button is disabled.

### Netlify Forms

```toml
[params]
supporters_form_provider = "netlify"
supporters_form_name = "supporters"
```

## Showing an up-to-date supporters list

Because your form provider stores submissions, the easiest workflow is:

1) Export a CSV of submissions from your form provider.
2) Convert it into Hugo’s data file with the included script:

```bash
python3 scripts/import_supporters_csv.py path/to/export.csv
```

This writes/updates `data/supporters.json`, which is rendered on the “Supporters” page.

Notes:
- The importer intentionally outputs a privacy-friendly display name (first name + last initial) and does not publish emails.
- If your CSV has different column names, tell me which provider/export you’re using and I can adapt the importer.

## Structure

- `config.toml` – site config + menu
- `content/` – Markdown pages
- `layouts/` – minimal templates (no theme)
- `static/css/main.css` – minimal styling
