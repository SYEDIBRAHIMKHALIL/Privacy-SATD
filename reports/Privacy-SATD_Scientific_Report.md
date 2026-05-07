# Privacy-SATD Miner: A First Empirical Pass on Privacy-Related Self-Admitted Technical Debt

## Abstract
This report documents the first run of the Privacy-SATD Miner on 50 open-source repositories. We aim to surface early signals of privacy-related self-admitted technical debt (PSATD) in developer artifacts. We focus on descriptive counts, distributions, and a lightweight GDPR article mapping to support later manual review. We treat these results as exploratory and avoid compliance claims.

## Research Questions
- RQ1: Can a lightweight, keyword-driven pipeline surface PSATD signals across a curated OSS set?
- RQ2: Which sources and keywords dominate PSATD signals in the first run?
- RQ3: Which GDPR article mappings appear most often in the filtered set?

## Background and Related Work
Work on security-oriented SATD shows that developer self-admissions can surface actionable security signals. Diaz Ferreyra, Shahin, Zahedi, Quadri, and Prof. Riccardo Scandariato report this effect in their MSR 2024 study on security SATD (DOI: 10.1145/3643991.3644909). We use that work as a conceptual analogue and reposition the focus on privacy.

Privacy as Code research remains early relative to security as code. Diaz Ferreyra, Khelifi, Arachchilage, and Prof. Riccardo Scandariato synthesize the literature in a rapid review and highlight the lack of benchmarks and usability studies (arXiv:2412.16667). That gap motivates a data-first pipeline that can later support human validation and dataset curation.

## Data and Repository Selection
We curated 50 repositories with a Germany-first selection strategy and a Europe fallback. The list prioritizes security and privacy themes, enforces a minimum star threshold, and balances languages to avoid over-concentration. The repository list is stored in [../data/seed_repos.txt](../data/seed_repos.txt).

## Methodology
We collect commit messages, pull requests, issues, and commit comments for each repository. We normalize and compact text fields, then filter instances using a privacy keyword list. We map each filtered instance to GDPR articles via keyword overlap. This approach favors recall to build an initial candidate set for later labeling.

Pipeline summary:
- Input: repo list, max_items per source, privacy keyword list, GDPR article list.
- Processing: collect, normalize, filter, map GDPR articles.
- Output: JSONL, CSV, report, figures, and a dashboard dataset.

## Results
The first run produced 186 filtered instances across 35 unique repositories. Pull requests dominated the sources, followed by issues and commits. The top keywords were tracking, encryption, and consent. GDPR mapping skewed toward Art.32, then Art.6 and Art.7. These outcomes reflect the keyword design and the repository selection, not evidence of compliance or non-compliance.

Summary metrics (from [../data/results/report.json](../data/results/report.json)):

| Metric | Value |
| --- | --- |
| Total filtered instances | 186 |
| Unique repositories | 35 |
| Pull requests | 100 |
| Issues | 53 |
| Commits | 29 |
| Commit comments | 4 |

Top keywords:
- tracking: 96
- encryption: 56
- consent: 23

GDPR mapping counts:
- Art.32: 55
- Art.6: 25
- Art.7: 24
- Art.5: 3

Figures:
- Top repositories: [../data/results/figures/top_repos.png](../data/results/figures/top_repos.png)
- Top keywords: [../data/results/figures/top_keywords.png](../data/results/figures/top_keywords.png)
- Source types: [../data/results/figures/source_types.png](../data/results/figures/source_types.png)
- GDPR mapping: [../data/results/figures/gdpr_articles.png](../data/results/figures/gdpr_articles.png)
- Dashboard snapshot: [../data/results/figures/dashboard.png](../data/results/figures/dashboard.png)

## Discussion
Tracking and encryption dominate the keyword distribution. This pattern suggests that PSATD signals often cluster around telemetry, analytics, or transport security concerns. The presence of these terms does not indicate legal violations. It indicates developer self-admissions that merit review.

Pull requests are the strongest signal source in this run. PRs often contain longer, contextual descriptions that expose TODOs and design tradeoffs. This may explain their higher yield compared to commits. We will validate this pattern with manual labels.

## Limitations and Threats to Validity
The keyword filter can produce false positives and false negatives. The pipeline does not normalize for repo size, activity, or maintainer practices. We have not completed manual validation yet, so the results are descriptive. Network instability can also reduce completeness when paging the GitHub API.

## Reproducibility
The environment is defined in [../environment.yml](../environment.yml). The primary run used max_items=100 to avoid paging failures. Commands are documented in [../README.md](../README.md). Raw and filtered outputs are stored in [../data/results](../data/results).

## Ethics and Responsible Use
This project uses public OSS artifacts and does not attempt to deanonymize contributors. The results are not a compliance audit and should not be used to target projects or individuals. We treat the pipeline as an early signal system for research and tool development.

## Future Work
We plan to label a subset of instances with two annotators and compute precision and recall. We will extend GDPR mapping with sentence-level semantic similarity once we have labels. We also plan a usability study with practitioners to quantify false positive burden and interpretability.

## References
1. Nicolas E. Diaz Ferreyra, Mojtaba Shahin, Mansooreh Zahedi, Sodiq Quadri, and Riccardo Scandariato. What Can Self-Admitted Technical Debt Tell Us About Security? MSR 2024. DOI: 10.1145/3643991.3644909
2. Nicolas E. Diaz Ferreyra, Sirine Khelifi, Nalin Arachchilage, and Riccardo Scandariato. The Good, the Bad, and the (Un)Usable: A Rapid Literature Review on Privacy as Code. arXiv:2412.16667
