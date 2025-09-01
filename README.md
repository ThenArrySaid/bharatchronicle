# Bharat Chronicle Automated News Portal

This folder contains a self‑contained website template for **Bharat Chronicle**.  It
extends the prototype design you saw on Instagram by introducing a dynamic
“river of news” experience, automated content generation, advertising
placeholders and newsletter signup.  No coding experience is required to run
the site—simply unpack the ZIP archive and open `index.html` in your browser.

## Key Features

1. **Dynamic News Feed**  
   News stories are loaded from a JSON file (`data/news.json`) when the page
   loads.  As you scroll, additional stories are appended automatically,
   recreating the infinite stream popularised by modern news portals.  Ads
   placeholders are inserted after every four stories.

2. **Automated Content Generation**  
   To keep your site up to date without writing code, a helper script
   `fetch_news.py` is included.  Run the script on your own computer with
   network access to download headlines from any RSS or Atom feed and write
   them into `data/news.json`.  You can schedule the script (e.g. via cron on
   Linux or Task Scheduler on Windows) to refresh the news automatically.

   If you host your site on GitHub, a ready‑to‑use GitHub Actions workflow
   (`.github/workflows/news_update.yml`) is provided.  The workflow runs
   every six hours, executes `fetch_news.py` using a curated list of
   pro‑India feeds, and commits the updated `news.json` back to the
   repository.  You can trigger it manually or adjust the schedule as
   needed.  Note that the workflow only works when the repository has
   permission to push changes (for example, on your own fork).

3. **Adsense Ready**  
   Ad slots are marked in the feed with an `Advertisement` placeholder.  Once
   your Google AdSense account is approved, replace these placeholders with
   the `<script>` and `<ins>` tags provided by AdSense to start earning
   revenue.  A dashed border highlights the ad area until then.

4. **Newsletter Subscription**  
   The site includes a newsletter signup form.  Currently the form displays a
   friendly thank‑you message upon submission.  To collect real emails,
   integrate with a mailing list provider such as [Mailchimp], [Brevo] or
   [MailerLite] by replacing the form’s `action` attribute and hidden fields.

5. **Editorial Standards & Legal Pages**
   A new “Our Commitment to Integrity” section outlines Bharat Chronicle’s
   editorial values—accuracy, fairness and a pro‑India perspective.  This
   message helps readers understand your mission.  The repository also
   includes dedicated pages for **About**, **Privacy Policy** and **Terms &
   Conditions** (`about.html`, `privacy.html` and `terms.html`) so you can
   comply with legal requirements and give visitors more context about your
   publication.

## How to Refresh the News

1. Install the **feedparser** library:

   ```bash
   pip install feedparser
   ```

2. Run the `fetch_news.py` script with your chosen RSS feed URL:

   ```bash
   python fetch_news.py --feed_url https://feeds.bbci.co.uk/news/world/rss.xml --limit 20
   ```

   The script will create (or overwrite) `data/news.json` with the most
   recent items.  Once updated, simply refresh your browser—the site will
   display the latest headlines.

3. To automate updates, schedule the script to run at regular intervals.

   Alternatively, if you’re using GitHub to host your site, enable the
   provided GitHub Actions workflow.  Navigate to the **Actions** tab in
   your repository and enable workflows.  The `news_update` workflow will
   fetch fresh news every six hours and push changes automatically.  You can
   customise the cron schedule or provide your own feed list via workflow
   inputs.

## Customising the Site

- **Colour Palette & Typography:**  The colours are defined at the top of
  `style.css` using CSS variables.  Adjust `--primary`, `--secondary` and
  related variables to tweak the look and feel.
- **Hero Section:**  The hero image lives in `images/hero.png`.  Replace it
  with another background to fit your brand.
- **Posts Images:**  If RSS items don’t include a thumbnail, the script uses
  local fallback images (`post1.png`–`post4.png`).  Add more images or adjust
  the cycling logic in `script.js` to customise the visuals.
- **Advertising:**  Once approved for AdSense, replace the ad placeholders in
  `script.js` or insert the AdSense script directly in `index.html`.
- **Newsletter Form:**  To integrate a real mailing list, edit the
  `<form>` tag in `index.html` with the embed code provided by your
  newsletter provider.

## Caveats

This environment blocks network access, so the fetch script cannot be run here.
To see live news on your local machine, run `fetch_news.py` in an environment
with internet connectivity.  The sample `news.json` included here contains
placeholder articles to demonstrate functionality.