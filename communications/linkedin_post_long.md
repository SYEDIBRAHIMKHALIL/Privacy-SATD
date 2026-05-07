Privacy-SATD Miner: first results

We ran a Germany-first OSS scan to surface privacy-related self-admitted technical debt. The pipeline collects PRs, issues, commits, and comments, then filters candidates and maps them to GDPR articles with a lightweight heuristic.

First run highlights:
- 186 filtered instances across 35 repos
- Top keywords: tracking, encryption, consent
- GDPR mapping skewed toward Art.32, then Art.6 and Art.7

This is an early signal dataset, not a compliance audit. We plan to add manual labeling, measure precision and recall, and evaluate false positives with practitioners.

If you are working on privacy tooling, I would value feedback on keyword coverage and false positives.

References:
DOI: 10.1145/3643991.3644909
arXiv:2412.16667

Links:
Website: [WEBSITE URL]
GitHub: https://github.com/SYEDIBRAHIMKHALIL/Privacy-SATD
