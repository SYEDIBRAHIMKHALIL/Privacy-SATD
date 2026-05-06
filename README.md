# Privacy as Code: Privacy-SATD Miner

Python pipeline that mines GitHub repositories for self-admitted technical debt related to privacy, filters candidates, supports manual validation, and maps findings to GDPR articles.

## Why this project
- Mirrors MSR 2024 SATD methodology but targets privacy
- Produces candidate Privacy-SATD instances from code comments and developer text
- Supports Label Studio for two-annotator validation

## Environment
conda env create -f environment.yml
conda activate Privacy-SATD

Optional ML stack (for future model work):
python -m pip install -r requirements-ml.txt

## Setup
1. Create a virtual environment
2. Install dependencies: python -m pip install -r requirements.txt
3. Copy .env.example to .env and set tokens
4. Add repos to data/seed_repos.txt

## Repo discovery
python scripts/discover_repos.py --out data/seed_repos.txt --target-count 50 --min-stars 100

## Run
conda run -n Privacy-SATD python run_pipeline.py --repos data/seed_repos.txt --out-jsonl data/results/raw.jsonl

## Report and figures
conda run -n Privacy-SATD python run_pipeline.py --repos data/seed_repos.txt --label-studio-out data/results/label_studio_tasks.json --report-out data/results/report.md --report-json data/results/report.json --figures-dir data/results/figures --examples-out data/results/examples.json

## Label Studio (local)
1. pip install label-studio
2. label-studio start
3. python run_pipeline.py --repos data/seed_repos.txt --label-studio-out data/results/label_studio_tasks.json

## Outputs
- data/results/raw.jsonl
- data/results/filtered.jsonl
- data/results/label_studio_tasks.json
- data/results/results.csv
- data/results/summary.json
- data/results/report.md
- data/results/report.json
- data/results/figures/top_repos.png
- data/results/figures/top_keywords.png
- data/results/figures/source_types.png
- data/results/figures/gdpr_articles.png
- data/results/examples.json

## Dashboard
1. Run the pipeline to generate data/results/report.json and examples.json
2. Start a local server from the project root:
	python -m http.server 8000
3. Open http://localhost:8000/dashboard/index.html

Deployment:
- Copy dashboard/ and data/results/ to your website host
- If your host uses a different data path, edit DATA_BASE in dashboard/app.js

## References
- Nicolas E. Diaz Ferreyra, Mojtaba Shahin, Mansooreh Zahedi, Sodiq Quadri, Riccardo Scandariato. What Can Self-Admitted Technical Debt Tell Us About Security? MSR 2024. DOI: 10.1145/3643991.3644909
- Nicolas E. Diaz Ferreyra, Sirine Khelifi, Nalin Arachchilage, Riccardo Scandariato. The Good, the Bad, and the (Un)Usable: A Rapid Literature Review on Privacy as Code. arXiv:2412.16667

