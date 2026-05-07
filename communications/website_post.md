# Privacy-SATD Miner: First Results from a Germany-First OSS Scan

## Short Abstract
We built a pipeline to surface privacy-related self-admitted technical debt (PSATD) in open-source repositories. This first run uses 50 repositories, a keyword filter, and a lightweight GDPR mapping. The goal is to create an early signal dataset that can later support manual validation and deeper analysis.

## Why This Project
Privacy as Code remains early compared to security as code. The MSR 2024 SATD security study by Diaz Ferreyra, Shahin, Zahedi, Quadri, and Prof. Riccardo Scandariato, together with the PaC rapid review by Diaz Ferreyra, Khelifi, Arachchilage, and Prof. Scandariato, motivated a privacy-focused analogue on public OSS artifacts. This project does not assess compliance. It aims to observe where developers articulate privacy gaps in their own words.

## Key Findings from the First Run
- Filtered instances: 186
- Unique repositories: 35
- Top keywords: tracking, encryption, consent
- Top GDPR mappings: Art.32, Art.6, Art.7

## Visuals
- Top repositories: data/results/figures/top_repos.png
- Top keywords: data/results/figures/top_keywords.png
- Source types: data/results/figures/source_types.png
- GDPR mapping: data/results/figures/gdpr_articles.png
- Dashboard snapshot: data/results/figures/dashboard.png

## Methods in One Paragraph
The pipeline collects commit messages, pull requests, issues, and commit comments from a curated repository list. It normalizes text, applies a privacy keyword filter, and maps each candidate to GDPR articles through keyword overlap. We then generate a report and a static dashboard for review.

## Call to Action
If you are working on privacy tooling, I would value feedback on keyword coverage and false positives.

## Links
- Project page: [WEBSITE URL]
- GitHub: https://github.com/SYEDIBRAHIMKHALIL/Privacy-SATD

## References
- Diaz Ferreyra, Shahin, Zahedi, Quadri, Scandariato. MSR 2024. DOI: 10.1145/3643991.3644909
- Diaz Ferreyra, Khelifi, Arachchilage, Scandariato. arXiv:2412.16667
