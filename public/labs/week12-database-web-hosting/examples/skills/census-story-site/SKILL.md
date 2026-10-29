---
name: census-story-site
description: Build or revise a static class website from supplied Census teaching-analysis exports. Use for repeated Census story-site tasks, rather than live database apps or unrelated websites.
---

Read the supplied exports and the student's requested audience and scope before choosing content. Use actual values from the files; do not invent missing statistics or claim that sample-dot counts estimate population.

For this class, the source is a thinned synthetic 2010 Census dot extract and historical 2015 Pennsylvania districts. Explain these limitations near the visualizations. Keep source category labels consistent with the exported data.

Prefer a simple `index.html`, `styles.css`, and `app.js` when the student wants the class's static workflow. Read the supplied `assets/category_counts.json`, `assets/district_counts.csv`, and `assets/district_sample_map.png`; use relative asset links that also work under a GitHub Pages repository path. Do not add API credentials or an application backend to show already exported results.

Use semantic HTML and readable labels. If adding interactions, make them keyboard accessible. Show a useful error if an asset fails to load. Verify data totals against the export, local asset loading, and the page at a narrow viewport.

Preview locally with `python -m http.server 8000 --bind 127.0.0.1`. Explain the localhost URL and report what was tested. Follow the student's explicit choices if they request another structure. Push commits or publish only when those actions are requested; generating a local site alone does not request deployment.
