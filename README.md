# Srilakshmi's research blog

A Quarto website intended for https://srimed.github.io. Hosting uses GitHub Pages; no paid services are required.

## First-time publishing

1. Sign in to the `SriMed` GitHub account.
2. Check whether `SriMed/SriMed.github.io` already exists. If it does, inspect it before making changes. Otherwise create a **public** repository named `SriMed.github.io` without an initial README.
3. Push the contents of this folder to the repository's `main` branch, including `.github/workflows/publish.yml` and `.gitignore`.
4. In **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**.
5. In **Actions → Publish site**, run the workflow if the initial push happened before Pages was enabled.
6. Wait for both the build and deployment to pass, then open https://srimed.github.io.

## Write a post

Copy `templates/post.qmd` to `posts/your-post-slug/index.qmd`. Edit the title, description, date, categories, and body. Add figures in the same folder and refer to them with Markdown, for example `![Plot description](plot.png)`.

The template starts with `draft: true`; change it to `draft: false` when ready to publish. Drafts are omitted from the rendered site, but **source files committed to a public repository are public**, including drafts. Keep private work outside this repository.

Push to `main` to publish. The writing archive and RSS feed update automatically. Static code examples use normal fenced blocks such as ` ```python `; executable Python/R code is disabled initially. Enable execution only when the required environment and dependencies are specified in the publishing workflow. Do not commit generated caches or run output.

## Preview locally

Install [Quarto](https://quarto.org/docs/get-started/), then run `quarto preview` in this folder. `quarto render` checks the build without publishing. Generated files in `_site` are ignored by Git.

## Personalize

- `index.qmd`: introduction and selected work.
- `about.qmd`: bio and links.
- `_quarto.yml`: title, navigation, and site URL.
- `theme.scss`: typography and colors.

The starting copy uses your public GitHub name and RAG Forensics description. Review it before publishing.

## Add a domain later

Once the site is live, set a custom domain in GitHub Pages settings, configure your registrar's DNS following [GitHub's custom-domain guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site), and update `website.site-url` in `_quarto.yml` to the new HTTPS address.

## Setup references

The build follows [Quarto's GitHub Pages guidance](https://quarto.org/docs/publishing/github-pages.html) and [GitHub's custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). Post listings and RSS follow [Quarto's blog documentation](https://quarto.org/docs/websites/website-blog.html). Generated HTML is deployed as a workflow artifact, so the source repository does not need rendered output or a `gh-pages` branch.
