# Srilakshmi Medarametla

Source for [srimed.github.io](https://srimed.github.io/), built with [Quarto](https://quarto.org/docs/websites/) and hosted on [GitHub Pages](https://docs.github.com/en/pages).

## Preview

Install [Quarto](https://quarto.org/docs/get-started/), then run:

```sh
quarto preview
```

## Publish a post

Copy `templates/post.qmd` to `posts/your-post-slug/index.qmd`, update its metadata, and write the post. Set `draft: false` when ready.

Changes pushed to `main` automatically build and publish the site.

## Schedule an essay

Set `draft: false` and set `date` to the desired publication day in `YYYY-MM-DD` format, then push to `main`. Posts become eligible at **8 a.m. America/New_York** on that date, including daylight saving changes. `draft: true` always keeps an essay unpublished, regardless of its date.

The daily GitHub Actions check compares eligible posts with `publication-state.json` on the deployed site. If nothing is due, it skips Quarto and deployment. Failed or missed publications remain due for the next check. Pushes and manual workflow runs always rebuild, with future posts hidden until their release time.

GitHub documents [timezone-aware schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule) and notes that [scheduled runs can be delayed or dropped and are disabled after 60 days of repository inactivity](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). For an essay scheduled more than 60 days ahead, ensure the workflow remains enabled in Actions. You can also use **Actions → Publish site → Run workflow** to retry a due publication.

Production builds use [Quarto's website drafts](https://quarto.org/docs/websites/website-drafts.html) to hide unreleased content from pages, listings, search, feeds, and the sitemap. The source files in this public repository remain publicly readable before publication. Local `quarto preview` intentionally shows drafts and future posts.

To reproduce the production build locally (Python 3.9+):

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-build.txt
python scripts/publication.py render
```

Use this command instead of plain `quarto render` for date-gated output. The generated publication profile and `_site` output are not committed.
