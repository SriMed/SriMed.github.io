# Srilakshmi Medarametla

Source for [srimed.github.io](https://srimed.github.io/), built with [Quarto](https://quarto.org/docs/websites/) and hosted on [GitHub Pages](https://docs.github.com/en/pages).

## Preview

Install [Quarto](https://quarto.org/docs/get-started/), then run:

```sh
python3 scripts/reading.py --empty
quarto preview
```

## Publish a post

Copy `templates/post.qmd` to `posts/your-post-slug/index.qmd`, update its metadata, and write the post. Set `draft: false` when ready.

Changes pushed to `main` automatically build and publish the site.

## Schedule an essay

Set `draft: false` and set `date` to the desired publication day in `YYYY-MM-DD` format, then push to `main`. Posts become eligible at **8 a.m. America/New_York** on that date, including daylight saving changes. `draft: true` always keeps an essay unpublished, regardless of its date.

The daily GitHub Actions check compares eligible posts and the selected reading list with `publication-state.json` on the deployed site. If neither changes, it skips Quarto and deployment. Failed or missed publications remain due for the next check. Pushes and manual workflow runs always rebuild, with future posts hidden until their release time.

GitHub documents [timezone-aware schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule) and notes that [scheduled runs can be delayed or dropped and are disabled after 60 days of repository inactivity](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). For an essay scheduled more than 60 days ahead, ensure the workflow remains enabled in Actions. You can also use **Actions → Publish site → Run workflow** to retry a due publication.

Production builds use [Quarto's website drafts](https://quarto.org/docs/websites/website-drafts.html) to hide unreleased content from pages, listings, search, feeds, and the sitemap. The source files in this public repository remain publicly readable before publication. Local `quarto preview` intentionally shows drafts and future posts.

To reproduce the production build locally (Python 3.9+):

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-build.txt
python scripts/reading.py --empty
python scripts/publication.py render
```

Use this command instead of plain `quarto render` for date-gated output. The generated publication profile and `_site` output are not committed.

## Update the Content page

The Content page displays up to five entries explicitly checked **Show on website** in Notion, newest personal activity date first, then title for ties. It shows title, authors, original link, format, publication date, and a separate personal activity date or range. It does not display a separate progress label. It does not export notes, relations, page bodies, or unchecked entries. The existing Reading database can remain private. This uses [Notion's filtered data-source query API](https://developers.notion.com/reference/query-a-data-source), rather than publishing or embedding the database.

Create a [Notion internal connection](https://developers.notion.com/guides/get-started/create-a-notion-integration) with read-content access and grant it access to the Reading database. Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `NOTION_TOKEN`: the connection's API token.
- `NOTION_READING_DATA_SOURCE_ID`: the data source UUID (not its database/view ID).

The expected Notion properties are `Title` (title), `Authors` (text), `Link` (URL), `Type` (select: `Paper`, `Blog Post`, `Book`, `Report`, `Podcast`, or `Video`), `Progress` (select: `Done` or `In Progress`), `Date Read` (date), `Published` (text), and `Show on website` (checkbox). The existing `Date Read` property also stores listening and watching dates. The page labels these as personal activity dates separately from `Published`, which can hold a known year or an exact `YYYY-MM-DD` publication date. Missing dates are omitted; known personal activity dates appear as Read, Listened, or Watched in smaller italic text. Use date-only values, including date ranges; an in-progress range stays in progress until you change its status. Check up to five entries for a deliberate selection. Clearing all checkboxes publishes an empty list. The page explicitly presents these as highlights from a larger list.

The workflow syncs at the existing daily 8 a.m. New York check, on pushes to `main`, and on manual runs. To refresh sooner, run **Actions → Publish site → Run workflow**. Missing credentials or a failed sync stop deployment, leaving the last published site in place.

For a local preview with real readings, set the two environment variables and run `python scripts/reading.py` before `quarto preview`. For an offline preview, use `python scripts/reading.py --from-file /path/to/notion-response.json` with a local Notion API response. `--empty` deliberately clears the local preview list. The generated `_includes/reading.qmd` is ignored by Git; do not commit API responses or tokens. The private source remains in Notion, while the selected fields are public in the deployed HTML and search index.
