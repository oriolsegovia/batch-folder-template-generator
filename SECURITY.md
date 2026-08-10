# Security & privacy

## Do not commit

Never commit any of the following:

- real case or expediente identifiers;
- names, DNI/NIE, addresses or other personal data;
- internal administrative resolutions or reports;
- signed documents;
- organization-only templates;
- production `.exe` files that bundle private templates;
- local logs;
- local absolute paths;
- credentials, tokens or API keys.

## Important: bundled files are not secret

Packaging files inside a PyInstaller executable does **not** protect them cryptographically. An executable containing private PDFs/DOCX files must be treated as containing those files in recoverable form.

For public distribution, build only with dummy/public templates.

## Recommended workflow

Keep two separate workspaces:

1. **Public source repository** — generic code only.
2. **Private production workspace** — real templates and production builds.

Do not copy production documents into the public repository even temporarily, because Git history can preserve deleted content.

## Reporting

If confidential information is committed accidentally:

1. make the repository private immediately;
2. rotate any exposed secrets;
3. remove the content from Git history, not only from the latest commit;
4. review forks, releases and Actions artifacts.
