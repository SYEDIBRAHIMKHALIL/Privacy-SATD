# Dashboard

This is a static dashboard that reads the pipeline outputs and renders charts and example instances.

## Local preview
1. Run the pipeline to generate data/results/report.json and data/results/examples.json
2. Start a local server from the project root:
   python -m http.server 8000
3. Open http://localhost:8000/dashboard/index.html

## Deploy to a website
- Copy dashboard/ and data/results/ to your website host
- Keep report.json and examples.json accessible at data/results/
- If your site uses a different base path, update DATA_BASE in dashboard/app.js

## Notes
- The dashboard reads live JSON from the results folder
- Re-run the pipeline after changing the repository list
