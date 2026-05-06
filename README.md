# Privacy as Code: Privacy-SATD Miner

Python pipeline that mines GitHub repositories for self-admitted technical debt related to privacy, filters candidates, supports manual validation, and maps findings to GDPR articles.

## Why this project
- Mirrors MSR 2024 SATD methodology but targets privacy
- Produces candidate Privacy-SATD instances from code comments and developer text
- Supports Label Studio for two-annotator validation

## Setup
1. Create a virtual environment
2. Install dependencies: python -m pip install -r requirements.txt
3. Copy .env.example to .env and set tokens
4. Add repos to data/seed_repos.txt

## Repo discovery
python scripts/discover_repos.py --out data/seed_repos.txt --target-count 50 --min-stars 100

## Run
python run_pipeline.py --repos data/seed_repos.txt --out-jsonl data/results/raw.jsonl

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

